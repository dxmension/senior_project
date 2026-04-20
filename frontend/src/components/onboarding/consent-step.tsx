"use client";

import { useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";

interface ConsentStepProps {
  onNext: () => void;
}

const PRIVACY_TEXT = `Privacy Policy for nutrack Platform

This Privacy Policy describes how nutrack ("we", "our", or "us") collects, uses, and protects your personal information when you use our educational platform.

1. Information We Collect
We collect information you provide directly, including your Nazarbayev University email address, name, academic transcript data, course enrollments, and study progress. We also collect usage data such as login timestamps and feature interactions.

2. How We Use Your Information
Your information is used to provide personalized academic services, including GPA tracking, course recommendations, AI-powered study assistance, and deadline management. We analyze anonymized aggregate data to improve platform features.

3. Data Storage and Security
All personal data is stored securely on encrypted servers. Academic transcript data is processed and stored in structured format. We implement industry-standard security measures including JWT-based authentication and encrypted connections.

4. Data Sharing
We do not sell or share your personal information with third parties. Anonymized, aggregate statistics may be used for platform improvement and academic research with your consent.

5. Your Rights
You may request access to, correction of, or deletion of your personal data at any time through the platform settings or by contacting our support team.

6. Data Retention
Your data is retained for the duration of your enrollment at Nazarbayev University. You may request deletion of your account and associated data at any time.`;

const TERMS_TEXT = `Terms of Service for nutrack Platform

By using the nutrack platform, you agree to the following terms and conditions.

1. Eligibility
This platform is exclusively available to current students and staff of Nazarbayev University with valid @nu.edu.kz email addresses.

2. Account Responsibility
You are responsible for maintaining the confidentiality of your account credentials. You agree not to share your access with others or use the platform for unauthorized purposes.

3. Academic Data
By uploading your academic transcript, you consent to automated parsing and storage of your academic records for the purpose of providing personalized educational services. You are responsible for verifying the accuracy of parsed data.

4. AI-Generated Content
The AI study assistant provides recommendations and generated content for educational purposes only. AI-generated mock exams, flashcards, and study materials should be used as supplementary resources and do not replace official university materials.

5. Acceptable Use
You agree not to: upload malicious files, attempt to access other users' data, use the platform for commercial purposes, or interfere with platform operations.

6. Content Ownership
You retain ownership of your personal academic data. By using the platform, you grant us a limited license to process and display your data within the platform's services.

7. Service Availability
We strive to maintain platform availability but do not guarantee uninterrupted service. We reserve the right to modify or discontinue features with reasonable notice.

8. Limitation of Liability
nutrack is provided "as is" without warranties. We are not liable for academic decisions made based on platform data or AI recommendations.`;

export function ConsentStep({ onNext }: ConsentStepProps) {
  const [privacyChecked, setPrivacyChecked] = useState(false);
  const [termsChecked, setTermsChecked] = useState(false);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-1">
          Privacy Policy
        </h2>
        <GlassCard className="max-h-48 overflow-y-auto">
          <pre className="text-sm text-text-secondary whitespace-pre-wrap font-sans leading-relaxed">
            {PRIVACY_TEXT}
          </pre>
        </GlassCard>
        <label className="flex items-center gap-2 mt-3 cursor-pointer">
          <input
            type="checkbox"
            checked={privacyChecked}
            onChange={(e) => setPrivacyChecked(e.target.checked)}
            className="w-4 h-4 accent-[var(--accent-green)] rounded"
          />
          <span className="text-sm text-text-secondary">
            I have read and agree to the Privacy Policy
          </span>
        </label>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-1">
          Terms of Service
        </h2>
        <GlassCard className="max-h-48 overflow-y-auto">
          <pre className="text-sm text-text-secondary whitespace-pre-wrap font-sans leading-relaxed">
            {TERMS_TEXT}
          </pre>
        </GlassCard>
        <label className="flex items-center gap-2 mt-3 cursor-pointer">
          <input
            type="checkbox"
            checked={termsChecked}
            onChange={(e) => setTermsChecked(e.target.checked)}
            className="w-4 h-4 accent-[var(--accent-green)] rounded"
          />
          <span className="text-sm text-text-secondary">
            I have read and agree to the Terms of Service
          </span>
        </label>
      </div>

      <button
        onClick={onNext}
        disabled={!privacyChecked || !termsChecked}
        className="btn-primary w-full"
      >
        Continue
      </button>
    </div>
  );
}
