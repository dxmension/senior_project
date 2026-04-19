"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BookOpen,
  Search,
  Brain,
  UserCircle,
  Settings,
  X,
  CalendarDays,
} from "lucide-react";

const mainNav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/courses", label: "Courses", icon: BookOpen },
  { href: "/calendar", label: "Calendar", icon: CalendarDays },
  { href: "/catalog", label: "Catalog", icon: Search },
  { href: "/study", label: "Study Assistant", icon: Brain },
];

const bottomNav = [
  { href: "/profile", label: "Profile", icon: UserCircle },
  { href: "/settings", label: "Settings", icon: Settings },
];

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

export function Sidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname();

  const navLink = (item: (typeof mainNav)[0]) => {
    const active = pathname.startsWith(item.href);
    return (
      <Link
        key={item.href}
        href={item.href}
        onClick={onClose}
        className={`flex items-center gap-3 px-3 py-2.5 rounded-[var(--radius-sm)] text-sm font-medium transition-colors ${
          active
            ? "bg-accent-green-dim text-accent-green"
            : "text-text-secondary hover:text-text-primary hover:bg-bg-card"
        }`}
      >
        <item.icon size={18} />
        {item.label}
      </Link>
    );
  };

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      <aside
        className={`glass-sidebar fixed top-0 left-0 h-full w-60 z-50 flex flex-col transition-transform duration-200 lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between px-5 h-16 border-b border-border-primary">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-accent-green flex items-center justify-center">
              <span className="text-bg-primary font-bold text-sm">NU</span>
            </div>
            <span className="font-semibold text-text-primary">NU Learning</span>
          </Link>
          <button onClick={onClose} className="lg:hidden text-text-secondary hover:text-text-primary">
            <X size={20} />
          </button>
        </div>

        <nav className="flex-1 flex flex-col justify-between px-3 py-4">
          <div className="flex flex-col gap-1">{mainNav.map(navLink)}</div>
          <div className="flex flex-col gap-1 border-t border-border-primary pt-4">
            {bottomNav.map(navLink)}
          </div>
        </nav>
      </aside>
    </>
  );
}
