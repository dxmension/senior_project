"use client";

import { useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import { Spinner } from "@/components/ui/spinner";
import type { ApiResponse, TokenPair } from "@/types";

export default function AuthCallbackClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setTokens, fetchUser } = useAuthStore();
  const calledRef = useRef(false);

  useEffect(() => {
    if (calledRef.current) return;
    calledRef.current = true;

    const code = searchParams.get("code");
    if (!code) {
      router.replace("/login?error=missing_code");
      return;
    }

    (async () => {
      try {
        const res = await api.post<ApiResponse<TokenPair>>(
          "/auth/google-callback",
          { code }
        );
        const { access_token, refresh_token, is_onboarded } = res.data;
        setTokens(access_token, refresh_token);
        await fetchUser();
        router.replace(is_onboarded ? "/dashboard" : "/onboarding");
      } catch {
        router.replace("/login?error=auth_failed");
      }
    })();
  }, [searchParams, setTokens, fetchUser, router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <Spinner size={32} text="Signing you in..." />
    </div>
  );
}
