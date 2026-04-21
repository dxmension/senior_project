"use client";

import { useState, useRef, useEffect } from "react";
import { Menu, LogOut, UserCircle } from "lucide-react";
import Link from "next/link";
import { useAuthStore } from "@/stores/auth";
import { Avatar } from "@/components/ui/avatar";

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const { user, logout } = useAuthStore();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const displayName = user ? `${user.first_name} ${user.last_name}` : "";

  return (
    <header className="h-16 border-b border-border-primary flex items-center justify-between px-6 bg-bg-primary/80 backdrop-blur-md sticky top-0 z-30">
      <button
        onClick={onMenuClick}
        className="lg:hidden text-text-secondary hover:text-text-primary"
      >
        <Menu size={22} />
      </button>

      <div className="hidden lg:block" />

      <div className="relative" ref={dropdownRef}>
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="flex items-center gap-2 hover:opacity-80 transition-opacity"
        >
          <Avatar
            src={user?.avatar_url}
            name={displayName || "U"}
            size="sm"
          />
          <span className="text-sm text-text-secondary hidden sm:block">
            {displayName}
          </span>
        </button>

        {dropdownOpen && (
          <div className="absolute right-0 mt-2 w-48 glass-card-sm p-1 shadow-xl">
            <Link
              href="/profile"
              onClick={() => setDropdownOpen(false)}
              className="flex items-center gap-2 px-3 py-2 text-sm text-text-secondary hover:text-text-primary hover:bg-bg-card rounded-[var(--radius-sm)] transition-colors"
            >
              <UserCircle size={16} />
              Profile
            </Link>
            <div className="border-t border-border-primary my-1" />
            <button
              onClick={logout}
              className="flex items-center gap-2 px-3 py-2 text-sm text-accent-red hover:bg-accent-red-dim rounded-[var(--radius-sm)] transition-colors w-full"
            >
              <LogOut size={16} />
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
