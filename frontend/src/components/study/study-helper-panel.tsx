"use client";

import {
  AlertTriangle,
  ArrowLeft,
  BookOpen,
  Calendar,
  ChevronRight,
  Lightbulb,
  RefreshCw,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { GlassCard } from "@/components/ui/glass-card";
import { Spinner } from "@/components/ui/spinner";
import { api, getApiErrorMessage } from "@/lib/api";
import type { ApiResponse, EnrollmentItem } from "@/types";

interface TopicItem {
  name: string;
  source: "mindmap" | "material";
}

interface WeekOverview {
  week: number;
  summary: string;
  topics: TopicItem[];
  has_materials: boolean;
}

interface KeyPoint {
  id: string;
  label: string;
  short_description: string;
}

interface StudyGuideOverview {
  summary: string;
  key_points: KeyPoint[];
}

interface StudyGuide {
  id: number;
  topic: string;
  source_type: string;
  overview: StudyGuideOverview;
  details: Record<string, Record<string, string>>;
  created_at: string;
}

interface DetailResponse {
  point_id: string;
  explanation: string;
}

interface DeepDiveResponse {
  point_id: string;
  dive_type: string;
  content: string;
}

type Message =
  | { type: "bot-weeks" }
  | { type: "bot-week-overview"; data: WeekOverview }
  | { type: "bot-overview"; guide: StudyGuide }
  | { type: "bot-detail"; pointId: string; label: string; explanation: string }
  | { type: "bot-deep"; pointId: string; diveType: string; content: string }
  | { type: "bot-loading" }
  | { type: "bot-error"; text: string; retry?: () => void }
  | { type: "user-action"; text: string };

const WEEKS = Array.from({ length: 15 }, (_, i) => i + 1);

interface Props {
  enrollment: EnrollmentItem;
}

export function StudyHelperPanel({ enrollment }: Props) {
  const courseId = enrollment.course_id;
  const [messages, setMessages] = useState<Message[]>([
    { type: "bot-weeks" },
  ]);
  const [currentWeek, setCurrentWeek] = useState<number | null>(null);
  const [currentGuide, setCurrentGuide] = useState<StudyGuide | null>(null);
  const [warming, setWarming] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setWarming(true);
    api
      .post<ApiResponse<number[]>>(`/study-helper/${courseId}/warm`)
      .catch(() => {})
      .finally(() => setWarming(false));
  }, [courseId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  async function selectWeek(week: number) {
    setCurrentWeek(week);
    setCurrentGuide(null);
    setMessages((prev) => [
      ...prev,
      { type: "user-action", text: `Week ${week}` },
      { type: "bot-loading" },
    ]);
    try {
      const res = await api.post<ApiResponse<WeekOverview>>(
        `/study-helper/${courseId}/week/${week}`,
      );
      const data = res.data!;
      setMessages((prev) =>
        prev
          .filter((m) => m.type !== "bot-loading")
          .concat({ type: "bot-week-overview", data }),
      );
    } catch (err) {
      const msg = getApiErrorMessage(err, "Failed to load week overview");
      setMessages((prev) =>
        prev
          .filter((m) => m.type !== "bot-loading")
          .concat({
            type: "bot-error",
            text: msg,
            retry: () => void selectWeek(week),
          }),
      );
    }
  }

  async function selectTopic(topic: string) {
    setMessages((prev) => [
      ...prev,
      { type: "user-action", text: topic },
      { type: "bot-loading" },
    ]);
    try {
      const res = await api.post<ApiResponse<StudyGuide>>(
        `/study-helper/${courseId}/generate`,
        { topic, week: currentWeek },
      );
      const guide = res.data!;
      setCurrentGuide(guide);
      setMessages((prev) =>
        prev
          .filter((m) => m.type !== "bot-loading")
          .concat({ type: "bot-overview", guide }),
      );
    } catch (err) {
      const msg = getApiErrorMessage(err, "Failed to generate study guide");
      setMessages((prev) =>
        prev
          .filter((m) => m.type !== "bot-loading")
          .concat({
            type: "bot-error",
            text: msg,
            retry: () => void selectTopic(topic),
          }),
      );
    }
  }

  async function selectKeyPoint(pointId: string, label: string) {
    if (!currentGuide) return;
    setMessages((prev) => [
      ...prev,
      { type: "user-action", text: label },
      { type: "bot-loading" },
    ]);
    try {
      const res = await api.post<ApiResponse<DetailResponse>>(
        `/study-helper/${courseId}/guides/${currentGuide.id}/detail/${pointId}`,
      );
      const detail = res.data!;
      setMessages((prev) =>
        prev
          .filter((m) => m.type !== "bot-loading")
          .concat({ type: "bot-detail", pointId, label, explanation: detail.explanation }),
      );
    } catch (err) {
      const msg = getApiErrorMessage(err, "Failed to generate detail");
      setMessages((prev) =>
        prev
          .filter((m) => m.type !== "bot-loading")
          .concat({
            type: "bot-error",
            text: msg,
            retry: () => void selectKeyPoint(pointId, label),
          }),
      );
    }
  }

  async function requestDeepDive(pointId: string, diveType: string) {
    if (!currentGuide) return;
    const label = diveType === "explain_more" ? "Explain More" : "Give Example";
    setMessages((prev) => [
      ...prev,
      { type: "user-action", text: label },
      { type: "bot-loading" },
    ]);
    try {
      const res = await api.post<ApiResponse<DeepDiveResponse>>(
        `/study-helper/${courseId}/guides/${currentGuide.id}/deep/${pointId}?dive_type=${diveType}`,
      );
      const dive = res.data!;
      setMessages((prev) =>
        prev
          .filter((m) => m.type !== "bot-loading")
          .concat({ type: "bot-deep", pointId, diveType: dive.dive_type, content: dive.content }),
      );
    } catch (err) {
      const msg = getApiErrorMessage(err, "Failed to generate deep dive");
      setMessages((prev) =>
        prev
          .filter((m) => m.type !== "bot-loading")
          .concat({
            type: "bot-error",
            text: msg,
            retry: () => void requestDeepDive(pointId, diveType),
          }),
      );
    }
  }

  function goBackToWeeks() {
    setCurrentWeek(null);
    setCurrentGuide(null);
    setMessages([{ type: "bot-weeks" }]);
  }

  function goBackToWeekOverview() {
    setCurrentGuide(null);
    setMessages((prev) => {
      const idx = prev.findIndex((m) => m.type === "bot-week-overview");
      if (idx >= 0) return prev.slice(0, idx + 1);
      return prev;
    });
  }

  function goBackToOverview() {
    if (!currentGuide) return;
    setMessages((prev) => {
      const idx = prev.findIndex(
        (m) => m.type === "bot-overview" && m.guide.id === currentGuide.id,
      );
      if (idx >= 0) return prev.slice(0, idx + 1);
      return prev;
    });
  }

  return (
    <div className="flex flex-col" style={{ height: "calc(100vh - 280px)", minHeight: "400px" }}>
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto pr-2">
        {messages.map((msg, idx) => (
          <MessageBubble
            key={idx}
            message={msg}
            onSelectWeek={selectWeek}
            onSelectTopic={selectTopic}
            onSelectKeyPoint={selectKeyPoint}
            onDeepDive={requestDeepDive}
            onBackToWeeks={goBackToWeeks}
            onBackToWeekOverview={goBackToWeekOverview}
            onBackToOverview={goBackToOverview}
            isLast={idx === messages.length - 1}
            warming={warming}
          />
        ))}
      </div>
    </div>
  );
}

function MessageBubble({
  message,
  onSelectWeek,
  onSelectTopic,
  onSelectKeyPoint,
  onDeepDive,
  onBackToWeeks,
  onBackToWeekOverview,
  onBackToOverview,
  isLast,
  warming,
}: {
  message: Message;
  onSelectWeek: (week: number) => void;
  onSelectTopic: (topic: string) => void;
  onSelectKeyPoint: (id: string, label: string) => void;
  onDeepDive: (pointId: string, diveType: string) => void;
  onBackToWeeks: () => void;
  onBackToWeekOverview: () => void;
  onBackToOverview: () => void;
  isLast: boolean;
  warming: boolean;
}) {
  if (message.type === "user-action") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-accent-green/20 px-4 py-3 text-sm text-text-primary">
          {message.text}
        </div>
      </div>
    );
  }

  if (message.type === "bot-loading") {
    return (
      <div className="flex justify-start">
        <div className="max-w-[80%]">
          <GlassCard className="!py-4">
            <TypingIndicator />
          </GlassCard>
        </div>
      </div>
    );
  }

  if (message.type === "bot-error") {
    return (
      <div className="flex justify-start">
        <div className="max-w-[80%]">
          <GlassCard className="space-y-3 border-accent-red/30">
            <p className="text-sm text-accent-red">{message.text}</p>
            {message.retry && (
              <button
                type="button"
                onClick={message.retry}
                className="inline-flex items-center gap-1.5 rounded-full border border-border-primary bg-white/[0.03] px-3 py-1.5 text-xs text-text-secondary hover:border-accent-green/40 hover:text-text-primary"
              >
                <RefreshCw size={12} />
                Try again
              </button>
            )}
          </GlassCard>
        </div>
      </div>
    );
  }

  if (message.type === "bot-weeks") {
    return (
      <div className="flex justify-center">
        <div className="w-[80%]">
          <GlassCard className="space-y-4">
            <div className="flex items-center gap-2">
              <Calendar size={16} className="text-accent-green" />
              <p className="text-sm font-semibold text-text-primary">
                Choose a week to study
              </p>
            </div>
            {warming && (
              <p className="text-xs text-text-secondary animate-pulse">
                Preparing study guides...
              </p>
            )}
            <div className="grid grid-cols-3 gap-2 sm:grid-cols-5">
              {WEEKS.map((w) => (
                <button
                  key={w}
                  type="button"
                  onClick={() => onSelectWeek(w)}
                  disabled={!isLast}
                  className="group flex items-center justify-center rounded-xl border border-border-primary bg-white/[0.03] px-3 py-3 text-sm font-medium transition-all hover:border-accent-green/40 hover:bg-accent-green/5 disabled:opacity-50 disabled:pointer-events-none"
                >
                  <span className="text-text-primary">Week {w}</span>
                </button>
              ))}
            </div>
          </GlassCard>
        </div>
      </div>
    );
  }

  if (message.type === "bot-week-overview") {
    const { data } = message;
    return (
      <div className="flex justify-start">
        <div className="max-w-[90%]">
          <GlassCard className="space-y-4">
            <div>
              <p className="text-xs font-medium uppercase tracking-wider text-accent-green">
                Week {data.week} Overview
              </p>
              <p className="mt-2 text-sm leading-relaxed text-text-secondary">
                {data.summary}
              </p>
            </div>
            {!data.has_materials ? (
              <div className="flex items-start gap-2.5 rounded-xl border border-accent-orange/30 bg-accent-orange/5 px-4 py-3">
                <AlertTriangle size={14} className="mt-0.5 shrink-0 text-accent-orange" />
                <div>
                  <p className="text-sm font-medium text-accent-orange">
                    No materials uploaded for this week
                  </p>
                  <p className="mt-1 text-xs text-text-secondary">
                    Upload PDFs for this week to get content grounded in your actual coursework.
                  </p>
                </div>
              </div>
            ) : data.topics.length > 0 ? (
              <div>
                <p className="mb-2 text-xs font-semibold text-text-primary">
                  Topics
                </p>
                <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                  {data.topics.map((t) => (
                    <button
                      key={t.name}
                      type="button"
                      onClick={() => onSelectTopic(t.name)}
                      disabled={!isLast}
                      className="group flex items-center justify-between rounded-xl border border-border-primary bg-white/[0.03] px-4 py-3 text-left text-sm transition-all hover:border-accent-green/40 hover:bg-accent-green/5 disabled:opacity-50 disabled:pointer-events-none"
                    >
                      <span className="text-text-primary">{t.name}</span>
                      <div className="flex items-center gap-2">
                        <span className="rounded-full bg-white/[0.06] px-2 py-0.5 text-[10px] text-text-secondary">
                          {t.source}
                        </span>
                        <ChevronRight
                          size={14}
                          className="text-text-secondary transition-transform group-hover:translate-x-0.5"
                        />
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-sm text-text-secondary">
                No topics found for this week. Upload course materials or
                generate mindmaps first.
              </p>
            )}
            {isLast && (
              <button
                type="button"
                onClick={onBackToWeeks}
                className="inline-flex items-center gap-1.5 text-xs text-text-secondary hover:text-text-primary"
              >
                <ArrowLeft size={12} />
                Back to weeks
              </button>
            )}
          </GlassCard>
        </div>
      </div>
    );
  }

  if (message.type === "bot-overview") {
    const { guide } = message;
    return (
      <div className="flex justify-start">
        <div className="max-w-[90%]">
          <GlassCard className="space-y-4">
            <div>
              <p className="text-xs font-medium uppercase tracking-wider text-accent-green">
                {guide.topic}
              </p>
              <p className="mt-2 text-sm leading-relaxed text-text-secondary">
                {guide.overview.summary}
              </p>
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold text-text-primary">
                Key Points
              </p>
              <div className="space-y-2">
                {guide.overview.key_points.map((kp) => (
                  <button
                    key={kp.id}
                    type="button"
                    onClick={() => onSelectKeyPoint(kp.id, kp.label)}
                    disabled={!isLast}
                    className="group flex w-full items-start gap-3 rounded-xl border border-border-primary bg-white/[0.03] px-4 py-3 text-left transition-all hover:border-accent-green/40 hover:bg-accent-green/5 disabled:opacity-50 disabled:pointer-events-none"
                  >
                    <Lightbulb
                      size={14}
                      className="mt-0.5 shrink-0 text-accent-orange"
                    />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-text-primary">
                        {kp.label}
                      </p>
                      <p className="mt-0.5 text-xs text-text-secondary">
                        {kp.short_description}
                      </p>
                    </div>
                    <ChevronRight
                      size={14}
                      className="mt-0.5 shrink-0 text-text-secondary transition-transform group-hover:translate-x-0.5"
                    />
                  </button>
                ))}
              </div>
            </div>
            {isLast && (
              <button
                type="button"
                onClick={onBackToWeekOverview}
                className="inline-flex items-center gap-1.5 text-xs text-text-secondary hover:text-text-primary"
              >
                <ArrowLeft size={12} />
                Back to week overview
              </button>
            )}
          </GlassCard>
        </div>
      </div>
    );
  }

  if (message.type === "bot-detail") {
    return (
      <div className="flex justify-start">
        <div className="max-w-[90%]">
          <GlassCard className="space-y-4">
            <p className="text-xs font-medium uppercase tracking-wider text-accent-green">
              {message.label}
            </p>
            <div className="text-sm leading-relaxed text-text-secondary whitespace-pre-line">
              {message.explanation}
            </div>
            {isLast && (
              <div className="flex flex-wrap gap-2">
                <ActionButton
                  label="Explain More"
                  onClick={() => onDeepDive(message.pointId, "explain_more")}
                />
                <ActionButton
                  label="Give Example"
                  onClick={() => onDeepDive(message.pointId, "give_example")}
                />
                <button
                  type="button"
                  onClick={onBackToOverview}
                  className="inline-flex items-center gap-1.5 rounded-full border border-border-primary bg-white/[0.03] px-3 py-1.5 text-xs text-text-secondary hover:border-accent-green/40 hover:text-text-primary"
                >
                  <ArrowLeft size={12} />
                  Back to overview
                </button>
              </div>
            )}
          </GlassCard>
        </div>
      </div>
    );
  }

  if (message.type === "bot-deep") {
    const label =
      message.diveType === "explain_more" ? "Deeper Explanation" : "Examples";
    return (
      <div className="flex justify-start">
        <div className="max-w-[90%]">
          <GlassCard className="space-y-4">
            <p className="text-xs font-medium uppercase tracking-wider text-accent-orange">
              {label}
            </p>
            <div className="text-sm leading-relaxed text-text-secondary whitespace-pre-line">
              {message.content}
            </div>
            {isLast && (
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={onBackToOverview}
                  className="inline-flex items-center gap-1.5 rounded-full border border-border-primary bg-white/[0.03] px-3 py-1.5 text-xs text-text-secondary hover:border-accent-green/40 hover:text-text-primary"
                >
                  <ArrowLeft size={12} />
                  Back to overview
                </button>
                <button
                  type="button"
                  onClick={onBackToWeekOverview}
                  className="inline-flex items-center gap-1.5 rounded-full border border-border-primary bg-white/[0.03] px-3 py-1.5 text-xs text-text-secondary hover:border-accent-green/40 hover:text-text-primary"
                >
                  <ArrowLeft size={12} />
                  Back to week overview
                </button>
              </div>
            )}
          </GlassCard>
        </div>
      </div>
    );
  }

  return null;
}

function ActionButton({
  label,
  onClick,
}: {
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center gap-1.5 rounded-full bg-accent-green/10 px-3 py-1.5 text-xs font-medium text-accent-green hover:bg-accent-green/20"
    >
      {label}
      <ChevronRight size={12} />
    </button>
  );
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5">
      <span className="h-2 w-2 animate-bounce rounded-full bg-text-secondary [animation-delay:0ms]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-text-secondary [animation-delay:150ms]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-text-secondary [animation-delay:300ms]" />
    </div>
  );
}
