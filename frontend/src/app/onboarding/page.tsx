"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth";
import { ConsentStep } from "@/components/onboarding/consent-step";
import { UploadStep } from "@/components/onboarding/upload-step";
import { ConfirmStep } from "@/components/onboarding/confirm-step";
import { Spinner } from "@/components/ui/spinner";
import { GlassCard } from "@/components/ui/glass-card";
import type { ParsedTranscriptData } from "@/types";

type Step = "consent" | "upload" | "confirm";

const STEPS: Step[] = ["consent", "upload", "confirm"];
const STEP_LABELS: Record<Step, string> = {
  consent: "Consent",
  upload: "Upload",
  confirm: "Confirm",
};

export default function OnboardingPage() {
  const router = useRouter();
  const { isLoading, isAuthenticated, fetchUser } = useAuthStore();
  const [step, setStep] = useState<Step>("consent");
  const [parsedData, setParsedData] = useState<ParsedTranscriptData | null>(null);
  const [isManual, setIsManual] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.replace("/login");
      return;
    }
    fetchUser();
  }, [fetchUser, router]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner size={32} text="Loading..." />
      </div>
    );
  }

  if (!isAuthenticated) return null;

  const currentIdx = STEPS.indexOf(step);

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="w-12 h-12 rounded-xl bg-accent-green flex items-center justify-center">
              <span className="text-bg-primary font-bold text-lg">NU</span>
            </div>
          </div>
          <h1 className="text-2xl font-bold text-text-primary">
            Welcome to NU Learning
          </h1>
          <p className="text-sm text-text-secondary mt-1">
            Let&apos;s set up your profile
          </p>
        </div>

        <ProgressBar steps={STEPS} labels={STEP_LABELS} currentIdx={currentIdx} />

        <GlassCard className="mt-6">
          {step === "consent" && (
            <ConsentStep onNext={() => setStep("upload")} />
          )}
          {step === "upload" && (
            <UploadStep
              onNext={(data) => {
                setParsedData(data);
                setIsManual(false);
                setStep("confirm");
              }}
              onSkip={() => {
                setIsManual(true);
                setParsedData(null);
                setStep("confirm");
              }}
            />
          )}
          {step === "confirm" && (
            <ConfirmStep
              parsedData={parsedData}
              isManual={isManual}
              onDone={() => router.replace("/dashboard")}
            />
          )}
        </GlassCard>
      </div>
    </div>
  );
}

function ProgressBar({
  steps,
  labels,
  currentIdx,
}: {
  steps: Step[];
  labels: Record<Step, string>;
  currentIdx: number;
}) {
  return (
    <div className="flex items-center gap-2">
      {steps.map((s, i) => (
        <div key={s} className="flex items-center flex-1">
          <div className="flex items-center gap-2 flex-1">
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold shrink-0 ${
                i <= currentIdx
                  ? "bg-accent-green text-bg-primary"
                  : "bg-bg-card text-text-muted border border-border-primary"
              }`}
            >
              {i + 1}
            </div>
            <span
              className={`text-xs font-medium ${
                i <= currentIdx ? "text-text-primary" : "text-text-muted"
              }`}
            >
              {labels[s]}
            </span>
            {i < steps.length - 1 && (
              <div
                className={`flex-1 h-px mx-2 ${
                  i < currentIdx ? "bg-accent-green" : "bg-border-primary"
                }`}
              />
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
