import { NavLink as RouterNavLink, useLocation } from "react-router-dom";
import { Brain, Eye, FlaskConical, Activity } from "lucide-react";

const navItems = [
  { path: "/", label: "Command", icon: Brain },
  { path: "/vision", label: "Vision", icon: Eye },
  { path: "/synthesis", label: "Synthesis", icon: FlaskConical },
];

const TopNav = () => {
  const location = useLocation();

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-4"
      style={{ backdropFilter: "blur(24px)", background: "hsl(0 0% 4% / 0.95)", borderBottom: "1px solid hsl(0 0% 16%)" }}
    >
      <div className="flex items-center gap-2">
        <Activity className="w-5 h-5 text-crimson" />
        <span className="text-bone font-display font-bold text-lg tracking-tight">ResearchMind</span>
      </div>

      <div className="flex items-center gap-1">
        {navItems.map(({ path, label, icon: Icon }) => {
          const isActive = location.pathname === path;
          return (
            <RouterNavLink key={path} to={path}>
              <div
                className={`flex items-center gap-2 px-4 py-2 rounded-xl font-display text-sm font-medium transition-colors ${
                  isActive ? "text-crimson" : "text-bone/50 hover:text-bone/80"
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </div>
            </RouterNavLink>
          );
        })}
      </div>

      <div className="w-32" />
    </nav>
  );
};

export default TopNav;
