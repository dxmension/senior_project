"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { ApiResponse, CourseListItem } from "@/types";
import { Search, BookOpen, Edit2, Save, X } from "lucide-react";

interface CourseManagementProps {
  onUpdate: () => void;
}

export function CourseManagement({ onUpdate }: CourseManagementProps) {
  const [courses, setCourses] = useState<CourseListItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<CourseListItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [editingCourse, setEditingCourse] = useState<number | null>(null);
  const [editForm, setEditForm] = useState({
    title: "",
    department: "",
    ects: 0,
    description: "",
  });

  const loadAllCourses = async () => {
    setIsLoading(true);
    try {
      const res = await api.get<ApiResponse<CourseListItem[]>>(
        "/admin/courses?limit=100"
      );
      setCourses(res.data);
    } catch (err) {
      console.error("Failed to load courses:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const res = await api.get<ApiResponse<CourseListItem[]>>(
        `/admin/courses/search?q=${encodeURIComponent(searchQuery)}`
      );
      setSearchResults(res.data);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setIsSearching(false);
    }
  };

  const startEdit = (course: CourseListItem) => {
    setEditingCourse(course.id);
    setEditForm({
      title: course.title,
      department: course.department || "",
      ects: course.ects,
      description: "",
    });
  };

  const cancelEdit = () => {
    setEditingCourse(null);
    setEditForm({ title: "", department: "", ects: 0, description: "" });
  };

  const saveEdit = async (courseId: number) => {
    try {
      await api.patch(`/admin/courses/${courseId}`, editForm);
      setEditingCourse(null);
      onUpdate();

      // Refresh the list
      if (searchQuery.trim()) {
        await handleSearch();
      } else {
        await loadAllCourses();
      }
    } catch (err) {
      console.error("Update failed:", err);
      alert(err instanceof Error ? err.message : "Failed to update course");
    }
  };

  const displayedCourses = searchResults.length > 0 ? searchResults : courses;

  // Load all courses on mount
  useState(() => {
    loadAllCourses();
  });

  return (
    <div className="space-y-6">
      <div className="glass-card p-6">
        <h2 className="text-xl font-semibold text-text-primary mb-4 flex items-center gap-2">
          <BookOpen size={24} />
          Course Management
        </h2>

        <div className="flex gap-2 mb-4">
          <div className="relative flex-1">
            <Search
              className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary"
              size={18}
            />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Search by code or title..."
              className="w-full pl-10 pr-4 py-2 bg-bg-card border border-border-primary rounded-lg text-text-primary placeholder:text-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-green"
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={isSearching}
            className="px-4 py-2 bg-accent-green text-white rounded-lg hover:bg-accent-green/90 disabled:opacity-50"
          >
            {isSearching ? "..." : "Search"}
          </button>
          <button
            onClick={loadAllCourses}
            disabled={isLoading}
            className="px-4 py-2 bg-bg-card border border-border-primary text-text-primary rounded-lg hover:bg-bg-hover disabled:opacity-50"
          >
            {isLoading ? "..." : "Load All"}
          </button>
        </div>

        {isLoading && courses.length === 0 ? (
          <p className="text-center text-text-secondary py-8">Loading courses...</p>
        ) : displayedCourses.length === 0 ? (
          <p className="text-center text-text-secondary py-8">
            No courses found. Click "Load All" to view courses.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-border-primary">
                <tr>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-text-primary">
                    Code
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-text-primary">
                    Title
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-text-primary">
                    Department
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-text-primary">
                    ECTS
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-text-primary">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {displayedCourses.map((course) => (
                  <tr
                    key={course.id}
                    className="border-b border-border-primary hover:bg-bg-card"
                  >
                    {editingCourse === course.id ? (
                      <>
                        <td className="py-3 px-4 text-sm text-text-primary">
                          {course.code}
                        </td>
                        <td className="py-3 px-4">
                          <input
                            type="text"
                            value={editForm.title}
                            onChange={(e) =>
                              setEditForm({ ...editForm, title: e.target.value })
                            }
                            className="w-full px-2 py-1 bg-bg-card border border-border-primary rounded text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-green"
                          />
                        </td>
                        <td className="py-3 px-4">
                          <input
                            type="text"
                            value={editForm.department}
                            onChange={(e) =>
                              setEditForm({
                                ...editForm,
                                department: e.target.value,
                              })
                            }
                            className="w-full px-2 py-1 bg-bg-card border border-border-primary rounded text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-green"
                          />
                        </td>
                        <td className="py-3 px-4">
                          <input
                            type="number"
                            value={editForm.ects}
                            onChange={(e) =>
                              setEditForm({
                                ...editForm,
                                ects: parseInt(e.target.value) || 0,
                              })
                            }
                            className="w-20 px-2 py-1 bg-bg-card border border-border-primary rounded text-sm text-text-primary focus:outline-none focus:ring-1 focus:ring-accent-green"
                          />
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex gap-2">
                            <button
                              onClick={() => saveEdit(course.id)}
                              className="p-1 text-green-400 hover:bg-green-500/20 rounded"
                              title="Save"
                            >
                              <Save size={16} />
                            </button>
                            <button
                              onClick={cancelEdit}
                              className="p-1 text-text-secondary hover:bg-bg-hover rounded"
                              title="Cancel"
                            >
                              <X size={16} />
                            </button>
                          </div>
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="py-3 px-4 text-sm text-text-primary font-medium">
                          {course.code}
                        </td>
                        <td className="py-3 px-4 text-sm text-text-primary">
                          {course.title}
                        </td>
                        <td className="py-3 px-4 text-sm text-text-secondary">
                          {course.department || "—"}
                        </td>
                        <td className="py-3 px-4 text-sm text-text-secondary">
                          {course.ects}
                        </td>
                        <td className="py-3 px-4">
                          <button
                            onClick={() => startEdit(course)}
                            className="p-1 text-accent-green hover:bg-accent-green/20 rounded"
                            title="Edit"
                          >
                            <Edit2 size={16} />
                          </button>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
