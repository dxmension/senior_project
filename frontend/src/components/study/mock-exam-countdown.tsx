"use client";

import { Clock3 } from "lucide-react";
import { useEffect, useEffectEvent, useMemo, useRef, useState } from "react";

type TimedAttempt = {
  expires_at: string | null;
};

type MockExamCountdownProps = {
  expiresAt: string | null;
  label?: string;
  className?: string;
  onExpire?: () => void;
};

function secondsUntil(expiresAt: string, nowMs: number) {
  const deltaMs = new Date(expiresAt).getTime() - nowMs;
  return Math.max(Math.ceil(deltaMs / 1000), 0);
}

export function hasRunningTimer(attempt: TimedAttempt | null | undefined) {
  return Boolean(attempt?.expires_at);
}

export function formatCountdown(totalSeconds: number) {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  const parts = [minutes, seconds].map((value) => String(value).padStart(2, "0"));
  if (hours === 0) return parts.join(":");
  return [hours, ...parts].map((value) => String(value).padStart(2, "0")).join(":");
}

export function MockExamCountdown({
  expiresAt,
  label = "Time left",
  className = "",
  onExpire,
}: MockExamCountdownProps) {
  const [nowMs, setNowMs] = useState(() => Date.now());
  const handleExpire = useEffectEvent(() => {
    onExpire?.();
  });
  const hasExpiredRef = useRef(false);
  const secondsLeft = useMemo(() => {
    if (!expiresAt) return null;
    return secondsUntil(expiresAt, nowMs);
  }, [expiresAt, nowMs]);

  useEffect(() => {
    if (!expiresAt) return;
    hasExpiredRef.current = false;
    setNowMs(Date.now());
    const timer = window.setInterval(() => {
      setNowMs(Date.now());
    }, 1000);
    return () => window.clearInterval(timer);
  }, [expiresAt]);

  useEffect(() => {
    if (!expiresAt || secondsLeft !== 0 || hasExpiredRef.current) return;
    hasExpiredRef.current = true;
    handleExpire();
  }, [expiresAt, handleExpire, secondsLeft]);

  if (!expiresAt || secondsLeft == null) return null;

  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      <Clock3 size={14} />
      <span>
        {label}: {formatCountdown(secondsLeft)}
      </span>
    </div>
  );
}
