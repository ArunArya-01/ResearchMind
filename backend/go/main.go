package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"math"
	"math/rand"
	"net/http"
	"os"
	"runtime"
	"strconv"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

type Node struct {
	ID          int       `json:"id"`
	X           float64   `json:"x"`
	Y           float64   `json:"y"`
	Size        float64   `json:"size"`
	Connections []int     `json:"connections"`
	rng         *rand.Rand
}

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true },
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", withCORS(rootHandler))
	mux.HandleFunc("/nodes", withCORS(nodesHandler))
	mux.HandleFunc("/upload/pdf", withCORS(uploadProxyHandler))
	mux.HandleFunc("/ws/swarm", wsSwarmProxyHandler)

	port := getenv("GO_BACKEND_PORT", "8000")
	addr := ":" + port
	log.Printf("Go API listening on %s", addr)
	log.Printf("Python HTTP upstream: %s", pythonHTTPBaseURL())
	log.Printf("Python WS upstream: %s", pythonWSURL())

	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatalf("server failed: %v", err)
	}
}

func rootHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusNoContent)
		return
	}
	if r.Method != http.MethodGet {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	writeJSON(w, http.StatusOK, map[string]string{
		"status":  "ok",
		"message": "ResearchMind Go API Active",
	})
}

func nodesHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusNoContent)
		return
	}
	if r.Method != http.MethodGet {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	count := 200
	if q := r.URL.Query().Get("count"); q != "" {
		if parsed, err := strconv.Atoi(q); err == nil && parsed > 0 && parsed <= 5000 {
			count = parsed
		}
	}

	nodes := buildNodesConcurrent(count)
	writeJSON(w, http.StatusOK, nodes)
}

func buildNodesConcurrent(count int) []Node {
	nodes := make([]Node, count)
	workers := runtime.NumCPU()
	if workers < 2 {
		workers = 2
	}
	chunk := (count + workers - 1) / workers

	var wg sync.WaitGroup
	for worker := 0; worker < workers; worker++ {
		start := worker * chunk
		end := start + chunk
		if end > count {
			end = count
		}
		if start >= count {
			break
		}

		wg.Add(1)
		go func(seedOffset, from, to int) {
			defer wg.Done()
			rng := rand.New(rand.NewSource(time.Now().UnixNano() + int64(seedOffset*7919)))
			for i := from; i < to; i++ {
				angle := (float64(i)/float64(count))*math.Pi*2 + rng.Float64()*0.5
				radius := 120 + rng.Float64()*280
				nodes[i] = Node{
					ID:   i,
					X:    400 + math.Cos(angle)*radius + (rng.Float64()-0.5)*60,
					Y:    300 + math.Sin(angle)*radius + (rng.Float64()-0.5)*60,
					Size: 2 + rng.Float64()*4,
					rng:  rng,
				}
			}
		}(worker, start, end)
	}
	wg.Wait()

	for worker := 0; worker < workers; worker++ {
		start := worker * chunk
		end := start + chunk
		if end > count {
			end = count
		}
		if start >= count {
			break
		}

		wg.Add(1)
		go func(from, to int) {
			defer wg.Done()
			for i := from; i < to; i++ {
				numConns := 1 + int(nodes[i].rng.Float64()*3)
				nodes[i].Connections = make([]int, 0, numConns)
				for j := 0; j < numConns; j++ {
					target := int(nodes[i].rng.Float64() * float64(count))
					if target != i {
						nodes[i].Connections = append(nodes[i].Connections, target)
					}
				}
				nodes[i].rng = nil
			}
		}(start, end)
	}
	wg.Wait()

	return nodes
}

func uploadProxyHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		w.WriteHeader(http.StatusNoContent)
		return
	}
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	upstreamURL := fmt.Sprintf("%s/upload/pdf", pythonHTTPBaseURL())
	proxyReq, err := http.NewRequestWithContext(r.Context(), http.MethodPost, upstreamURL, r.Body)
	if err != nil {
		http.Error(w, fmt.Sprintf("proxy request build failed: %v", err), http.StatusInternalServerError)
		return
	}
	proxyReq.Header = r.Header.Clone()

	resp, err := (&http.Client{Timeout: 300 * time.Second}).Do(proxyReq)
	if err != nil {
		http.Error(w, fmt.Sprintf("python backend unavailable: %v", err), http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()

	copyHeaders(w.Header(), resp.Header)
	w.WriteHeader(resp.StatusCode)
	_, _ = io.Copy(w, resp.Body)
}

func wsSwarmProxyHandler(w http.ResponseWriter, r *http.Request) {
	clientConn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		return
	}

	upstream, _, err := websocket.DefaultDialer.DialContext(
		r.Context(),
		pythonWSURL(),
		http.Header{},
	)
	if err != nil {
		_ = clientConn.WriteJSON(map[string]string{
			"agent":   "System",
			"message": fmt.Sprintf("Unable to reach Python swarm service: %v", err),
		})
		_ = clientConn.Close()
		return
	}

	ctx, cancel := context.WithCancel(r.Context())
	defer cancel()

	var wg sync.WaitGroup
	wg.Add(2)

	go wsPump(ctx, &wg, cancel, clientConn, upstream)
	go wsPump(ctx, &wg, cancel, upstream, clientConn)

	wg.Wait()
	_ = clientConn.Close()
	_ = upstream.Close()
}

func wsPump(ctx context.Context, wg *sync.WaitGroup, cancel context.CancelFunc, from, to *websocket.Conn) {
	defer wg.Done()
	for {
		select {
		case <-ctx.Done():
			return
		default:
		}

		msgType, payload, err := from.ReadMessage()
		if err != nil {
			cancel()
			return
		}
		if err := to.WriteMessage(msgType, payload); err != nil {
			cancel()
			return
		}
	}
}

func withCORS(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "*")
		next(w, r)
	}
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

func copyHeaders(dst, src http.Header) {
	for k, vv := range src {
		if k == "Access-Control-Allow-Origin" || k == "Access-Control-Allow-Methods" || k == "Access-Control-Allow-Headers" {
			continue
		}
		for _, v := range vv {
			dst.Add(k, v)
		}
	}
}

func getenv(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}

func pythonHTTPBaseURL() string {
	return getenv("PYTHON_BACKEND_URL", "http://localhost:8001")
}

func pythonWSURL() string {
	return getenv("PYTHON_SWARM_WS_URL", "ws://localhost:8001/ws/swarm")
}
