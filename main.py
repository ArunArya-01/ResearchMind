import argparse
import os
from dotenv import load_dotenv
from core.ingestion import IngestionPipeline


def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="ResearchMind - AI Research Hypothesis Generator")
    parser.add_argument("--topic", type=str, required=True, help="Research topic to explore")
    parser.add_argument("--limit", type=int, default=5, help="Number of papers to fetch")
    parser.add_argument("--output", type=str, default="data/ingested.json", help="Output file path")
    
    args = parser.parse_args()
    
    print(f"ResearchMind Ingestion Pipeline")
    print(f"Topic: {args.topic}")
    print(f"Fetching up to {args.limit} papers...\n")
    
    pipeline = IngestionPipeline()
    results = pipeline.run(args.topic, limit=args.limit)
    
    print(f"\nProcessed {len(results)} papers successfully.")
    
    output_path = pipeline.save_results(results, args.output)
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
