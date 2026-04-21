"use client";

import { useEffect, useRef, useState } from "react";
import { Search, X, Brain, Layers, FileText } from "lucide-react";

import { api } from "@/lib/api";
import type {
  ApiResponse,
  GenerateMockOptions,
  MockExamDifficulty,
  SharedCourseMaterial,
  StudyMaterialUpload,
} from "@/types";

const PAGE_SIZE = 10;

const DEFAULT_QUESTION_COUNT: Record<string, number> = {
  quiz: 12,
  midterm: 20,
  final: 30,
};

type LibraryTab = "my_library" | "shared_library";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  courseId: number;
  assessmentType: string;
  onGenerate: (opts: GenerateMockOptions) => void;
}

function TabButton({
  active,
  label,
  onClick,
}: {
  active: boolean;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm transition-colors ${
        active
          ? "bg-accent-green text-bg-primary"
          : "border border-border-primary bg-white/[0.03] text-text-secondary hover:border-accent-green/40 hover:text-text-primary"
      }`}
    >
      {label}
    </button>
  );
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function GenerateMockPopup({
  isOpen,
  onClose,
  courseId,
  assessmentType,
  onGenerate,
}: Props) {
  const [activeTab, setActiveTab] = useState<LibraryTab>("my_library");
  const [uploads, setUploads] = useState<StudyMaterialUpload[]>([]);
  const [sharedMaterials, setSharedMaterials] = useState<SharedCourseMaterial[]>([]);
  const [selectedUploadIds, setSelectedUploadIds] = useState<Set<number>>(new Set());
  const [selectedSharedIds, setSelectedSharedIds] = useState<Set<number>>(new Set());
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [difficulty, setDifficulty] = useState<MockExamDifficulty>("medium");
  const [questionCount, setQuestionCount] = useState(
    DEFAULT_QUESTION_COUNT[assessmentType] ?? 20
  );
  const [includeRumoredQuestions, setIncludeRumoredQuestions] = useState(false);
  const [includeHistoricQuestions, setIncludeHistoricQuestions] = useState(false);
  const backdropRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    setActiveTab("my_library");
    setSearchQuery("");
    setPage(1);
    setLoading(true);

    void Promise.all([
      api.get<ApiResponse<StudyMaterialUpload[]>>(`/course-materials/${courseId}/uploads`),
      api.get<ApiResponse<SharedCourseMaterial[]>>(`/course-materials/${courseId}/library`),
    ]).then(([uploadsRes, sharedRes]) => {
      const completed = (uploadsRes.data ?? []).filter(
        (u) => u.upload_status === "completed"
      );
      setUploads(completed);
      setSharedMaterials(sharedRes.data ?? []);
      setSelectedUploadIds(new Set(completed.map((u) => u.id)));
      setSelectedSharedIds(new Set((sharedRes.data ?? []).map((m) => m.id)));
    }).finally(() => setLoading(false));
  }, [isOpen, courseId]);

  useEffect(() => {
    setPage(1);
  }, [searchQuery, activeTab]);

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    if (isOpen) document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const currentItems =
    activeTab === "my_library" ? uploads : sharedMaterials;

  const filtered = currentItems.filter((item) => {
    const name =
      activeTab === "my_library"
        ? (item as StudyMaterialUpload).original_filename
        : (item as SharedCourseMaterial).title;
    return name.toLowerCase().includes(searchQuery.toLowerCase());
  });

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageItems = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  function toggleItem(id: number) {
    if (activeTab === "my_library") {
      setSelectedUploadIds((prev) => {
        const next = new Set(prev);
        if (next.has(id)) next.delete(id);
        else next.add(id);
        return next;
      });
    } else {
      setSelectedSharedIds((prev) => {
        const next = new Set(prev);
        if (next.has(id)) next.delete(id);
        else next.add(id);
        return next;
      });
    }
  }

  function toggleAll() {
    if (activeTab === "my_library") {
      const allIds = new Set(filtered.map((i) => i.id));
      const allSelected = filtered.every((i) => selectedUploadIds.has(i.id));
      setSelectedUploadIds(allSelected ? new Set() : allIds);
    } else {
      const allIds = new Set(filtered.map((i) => i.id));
      const allSelected = filtered.every((i) => selectedSharedIds.has(i.id));
      setSelectedSharedIds(allSelected ? new Set() : allIds);
    }
  }

  function handleGenerate() {
    onGenerate({
      difficulty,
      question_count: questionCount,
      selected_upload_ids: Array.from(selectedUploadIds),
      selected_shared_material_ids: Array.from(selectedSharedIds),
      include_rumored_questions: includeRumoredQuestions,
      include_historic_questions: includeHistoricQuestions,
    });
  }

  const isItemSelected = (id: number) =>
    activeTab === "my_library"
      ? selectedUploadIds.has(id)
      : selectedSharedIds.has(id);

  const totalSelected = selectedUploadIds.size + selectedSharedIds.size;

  return (
    <div
      ref={backdropRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={(e) => {
        if (e.target === backdropRef.current) onClose();
      }}
    >
      <div className="relative flex w-full max-w-2xl flex-col rounded-2xl border border-border-primary bg-[rgba(18,18,18,0.98)] shadow-2xl mx-4 max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border-primary px-6 py-4">
          <div className="flex items-center gap-2">
            <Brain size={18} className="text-accent-green" />
            <h2 className="text-base font-semibold text-text-primary">
              Generate AI Mock Exam
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded p-1 text-text-secondary transition-colors hover:bg-white/5 hover:text-text-primary"
          >
            <X size={16} />
          </button>
        </div>

        {/* Controls row */}
        <div className="flex flex-wrap gap-4 border-b border-border-primary px-6 py-4">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-text-secondary">Questions</label>
            <input
              type="number"
              min={1}
              max={60}
              value={questionCount}
              onChange={(e) =>
                setQuestionCount(Math.max(1, Math.min(60, Number(e.target.value))))
              }
              className="w-20 rounded-lg border border-border-primary bg-white/[0.03] px-3 py-1.5 text-sm text-text-primary focus:border-accent-green/60 focus:outline-none"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-text-secondary">Difficulty</label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value as MockExamDifficulty)}
              className="rounded-lg border border-border-primary bg-[#161616] px-3 py-1.5 text-sm text-text-primary focus:border-accent-green/60 focus:outline-none"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          <div className="flex flex-col justify-end gap-2">
            <label className="flex cursor-pointer items-center gap-2 text-sm text-text-secondary hover:text-text-primary">
              <input
                type="checkbox"
                checked={includeRumoredQuestions}
                onChange={(e) => setIncludeRumoredQuestions(e.target.checked)}
                className="accent-[#a3e635]"
              />
              Add rumored questions
            </label>
            <label className="flex cursor-pointer items-center gap-2 text-sm text-text-secondary hover:text-text-primary">
              <input
                type="checkbox"
                checked={includeHistoricQuestions}
                onChange={(e) => setIncludeHistoricQuestions(e.target.checked)}
                className="accent-[#a3e635]"
              />
              Add historic questions
            </label>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 px-6 pt-4">
          <TabButton
            active={activeTab === "my_library"}
            label="My Library"
            onClick={() => setActiveTab("my_library")}
          />
          <TabButton
            active={activeTab === "shared_library"}
            label="Shared Library"
            onClick={() => setActiveTab("shared_library")}
          />
        </div>

        {/* Search */}
        <div className="px-6 pt-3">
          <div className="flex items-center gap-2 rounded-lg border border-border-primary bg-white/[0.03] px-3 py-2">
            <Search size={14} className="shrink-0 text-text-muted" />
            <input
              type="text"
              placeholder="Search materials..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 bg-transparent text-sm text-text-primary placeholder-text-muted focus:outline-none"
            />
          </div>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto px-6 py-3 min-h-0">
          {loading ? (
            <p className="py-8 text-center text-sm text-text-secondary">
              Loading materials...
            </p>
          ) : filtered.length === 0 ? (
            <p className="py-8 text-center text-sm text-text-secondary">
              {searchQuery ? "No materials match your search." : "No materials found."}
            </p>
          ) : (
            <>
              <div className="mb-2 flex items-center justify-between">
                <button
                  type="button"
                  onClick={toggleAll}
                  className="text-xs text-accent-green hover:underline"
                >
                  {filtered.every((i) => isItemSelected(i.id))
                    ? "Deselect all"
                    : "Select all"}
                </button>
                <span className="text-xs text-text-muted">
                  {filtered.length} file{filtered.length !== 1 ? "s" : ""}
                </span>
              </div>
              <div className="space-y-1">
                {pageItems.map((item) => {
                  const isUpload = activeTab === "my_library";
                  const upload = item as StudyMaterialUpload;
                  const shared = item as SharedCourseMaterial;
                  const name = isUpload ? upload.original_filename : shared.title;
                  const sub = isUpload
                    ? `Week ${upload.week} · ${formatFileSize(upload.file_size_bytes)}`
                    : `Week ${shared.week} · ${shared.original_filename}`;
                  const selected = isItemSelected(item.id);

                  return (
                    <label
                      key={item.id}
                      className={`flex cursor-pointer items-start gap-3 rounded-lg border px-3 py-2.5 transition-colors ${
                        selected
                          ? "border-accent-green/30 bg-accent-green/5"
                          : "border-border-primary bg-white/[0.02] hover:border-border-light"
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selected}
                        onChange={() => toggleItem(item.id)}
                        className="mt-0.5 accent-[#a3e635]"
                      />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm text-text-primary">{name}</p>
                        <p className="mt-0.5 text-xs text-text-muted">{sub}</p>
                      </div>
                      <FileText size={14} className="mt-0.5 shrink-0 text-text-muted" />
                    </label>
                  );
                })}
              </div>
            </>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between border-t border-border-primary px-6 py-2">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="text-xs text-text-secondary disabled:opacity-40 hover:text-text-primary disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="text-xs text-text-muted">
              {page} / {totalPages}
            </span>
            <button
              type="button"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              className="text-xs text-text-secondary disabled:opacity-40 hover:text-text-primary disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-border-primary px-6 py-4">
          <span className="text-xs text-text-muted">
            {totalSelected} material{totalSelected !== 1 ? "s" : ""} selected
          </span>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-border-primary px-4 py-2 text-sm text-text-secondary transition-colors hover:border-border-light hover:text-text-primary"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleGenerate}
              className="inline-flex items-center gap-2 rounded-lg bg-accent-green px-4 py-2 text-sm font-semibold text-bg-primary transition-opacity hover:opacity-90"
            >
              <Brain size={14} />
              Generate
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
