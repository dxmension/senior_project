import { Suspense } from "react";
import AuthCallbackClient from "./auth-callback-client";
import { Spinner } from "@/components/ui/spinner";

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><Spinner size={32} text="Signing you in..." /></div>}>
      <AuthCallbackClient />
    </Suspense>
  );
}
