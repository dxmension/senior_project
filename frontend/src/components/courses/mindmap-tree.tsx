"use client";

import { useEffect, useRef, useState } from "react";
import type React from "react";
import type { MindmapNode } from "@/types";

// ─── Constants ────────────────────────────────────────────────────────────────

const NW = 148; const NH = 38; const HGAP = 144; const UNIT = 56; const PAD = 32;
const CONTAINER_H = 700; const DESC_W = 300; const DESC_GAP = 10;
const NODE_GAP = 8; // minimum gap between node edges

// ─── Types ────────────────────────────────────────────────────────────────────

interface Offset { dx: number; dy: number; }
interface Viewport { zoom: number; panX: number; panY: number; }
interface Placed { node: MindmapNode; depth: number; x: number; y: number; children: Placed[]; }

type DragState =
  | { type: "canvas"; startX: number; startY: number; startPanX: number; startPanY: number }
  | { type: "node"; nodeIds: string[]; startX: number; startY: number; startOffsets: Map<string, Offset> };

// ─── Helpers ──────────────────────────────────────────────────────────────────

function off(id: string, offsets: Map<string, Offset>): Offset {
  return offsets.get(id) ?? { dx: 0, dy: 0 };
}

function estimateDescH(label: string, description: string): number {
  const innerW = DESC_W - 28;
  const labelLines = Math.max(1, Math.ceil((label.length * 7) / innerW));
  const body = description || "No description available.";
  const bodyLines = Math.max(1, Math.ceil((body.length * 5.8) / innerW));
  return labelLines * 18 + bodyLines * 16 + 24;
}

// ─── Palette ──────────────────────────────────────────────────────────────────

const PALETTE = [
  { fill: "#012d1b", stroke: "#00c48c", text: "#00c48c" },
  { fill: "#1c1c30", stroke: "#818cf8", text: "#818cf8" },
  { fill: "#1a2624", stroke: "#2dd4bf", text: "#2dd4bf" },
  { fill: "#1e1a24", stroke: "#c084fc", text: "#c084fc" },
  { fill: "#1c1c1c", stroke: "#6b7280", text: "#9ca3af" },
];

function palette(depth: number) { return PALETTE[Math.min(depth, PALETTE.length - 1)]; }

// ─── Layout ──────────────────────────────────────────────────────────────────
//
// Children are distributed using a flat UNIT spacing based only on the direct
// child count — NOT on recursive leaf counts. This keeps children clustered
// near the parent's y. Grandchildren expanding do not cause ancestors to shift.

function place(
  node: MindmapNode, depth: number, x: number, yMid: number, expanded: Set<string>,
): Placed {
  const result: Placed = { node, depth, x, y: yMid, children: [] };
  if (!node.children.length || !expanded.has(node.id)) return result;
  const n = node.children.length;
  for (let i = 0; i < n; i++) {
    const yOffset = i === 0 ? 0 : i * UNIT;
    result.children.push(
      place(node.children[i], depth + 1, x + NW + HGAP, yMid + yOffset, expanded),
    );
  }
  return result;
}

function findPlaced(p: Placed, id: string): Placed | null {
  if (p.node.id === id) return p;
  for (const c of p.children) { const f = findPlaced(c, id); if (f) return f; }
  return null;
}

function collectSubtreeIds(p: Placed): string[] {
  return [p.node.id, ...p.children.flatMap(collectSubtreeIds)];
}

function bounds(p: Placed, offsets: Map<string, Offset>): { x1: number; y1: number; x2: number; y2: number } {
  const o = off(p.node.id, offsets);
  let x1 = p.x + o.dx, y1 = p.y + o.dy - NH / 2, x2 = p.x + o.dx + NW, y2 = p.y + o.dy + NH / 2;
  for (const c of p.children) {
    const b = bounds(c, offsets);
    x1 = Math.min(x1, b.x1); y1 = Math.min(y1, b.y1);
    x2 = Math.max(x2, b.x2); y2 = Math.max(y2, b.y2);
  }
  return { x1, y1, x2, y2 };
}

// ─── Overlap-driven shifts ────────────────────────────────────────────────────

function pushSubtree(p: Placed, delta: number, next: Map<string, Offset>): void {
  const o = next.get(p.node.id) ?? { dx: 0, dy: 0 };
  next.set(p.node.id, { dx: o.dx, dy: o.dy + delta });
  p.children.forEach(c => pushSubtree(c, delta, next));
}

// Sweep nodes top-to-bottom: push each movable node down just enough to clear
// the one above it. Chains correctly — pushing A into B then pushes B too.
function sweepDown(
  nodes: Placed[],
  movable: Set<string>,
  next: Map<string, Offset>,
): void {
  const sorted = [...nodes].sort(
    (a, b) => (a.y + (next.get(a.node.id)?.dy ?? 0)) - (b.y + (next.get(b.node.id)?.dy ?? 0)),
  );
  for (let i = 1; i < sorted.length; i++) {
    const above = sorted[i - 1];
    const curr = sorted[i];
    if (!movable.has(curr.node.id)) continue;
    const aboveEffY = above.y + (next.get(above.node.id)?.dy ?? 0);
    const currEffY = curr.y + (next.get(curr.node.id)?.dy ?? 0);
    const gap = currEffY - aboveEffY;
    if (gap < NH + NODE_GAP) {
      const push = NH + NODE_GAP - gap;
      const o = next.get(curr.node.id) ?? { dx: 0, dy: 0 };
      next.set(curr.node.id, { dx: o.dx, dy: o.dy + push });
      curr.children.forEach(c => pushSubtree(c, push, next));
    }
  }
}

// When a description opens below node `opened`, push same-depth siblings that
// overlap with the panel, then sweep to resolve any secondary overlaps.
function applyDescriptionShift(
  prev: Map<string, Offset>,
  layout: Placed,
  opened: Placed,
  descH: number,
): Map<string, Offset> {
  const next = new Map(prev);
  const openedEffY = opened.y + (prev.get(opened.node.id)?.dy ?? 0);

  const descTop = openedEffY + NH / 2 + DESC_GAP;
  const descBottom = descTop + descH;

  const siblings: Placed[] = [];

  function visit(p: Placed, inheritedPush: number) {
    if (p.node.id === opened.node.id) {
      for (const c of p.children) visit(c, 0);
      return;
    }
    const pOff = next.get(p.node.id) ?? { dx: 0, dy: 0 };
    const pEffY = p.y + pOff.dy;

    let push = inheritedPush;
    if (push === 0 && p.depth === opened.depth) {
      siblings.push(p);
      const nodeTop = pEffY - NH / 2;
      const nodeBottom = pEffY + NH / 2;
      const overlaps = nodeTop < descBottom && nodeBottom > descTop;
      if (overlaps) push = descBottom - nodeTop + NODE_GAP;
    }

    if (push > 0) next.set(p.node.id, { dx: pOff.dx, dy: pOff.dy + push });
    for (const c of p.children) visit(c, push);
  }

  visit(layout, 0);

  // Second pass: resolve any overlaps between siblings caused by the first push
  const movable = new Set(siblings.map(s => s.node.id));
  sweepDown(siblings, movable, next);

  return next;
}

// When a node is expanded, merge new children (immovable) with existing nodes
// at the same depth, then sweep top-to-bottom to resolve all overlaps.
function applyExpansionShift(
  prev: Map<string, Offset>,
  oldLayout: Placed,
  newChildren: Placed[],
  skipIds: Set<string>,
  newLayout: Placed,
): Map<string, Offset> {
  if (newChildren.length === 0) return prev;
  const childDepth = newChildren[0].depth;
  const next = new Map(prev);

  // Find the parent of the new children in the new layout and inherit its current offset
  let parentId: string | null = null;
  function findParentByDepth(p: Placed, targetDepth: number): Placed | null {
    if (p.depth === targetDepth - 1) {
      // Check if this parent has children matching our new children
      const hasMatchingChildren = p.children.some(pc => 
        newChildren.some(nc => nc.node.id === pc.node.id)
      );
      if (hasMatchingChildren) return p;
    }
    for (const c of p.children) {
      const found = findParentByDepth(c, targetDepth);
      if (found) return found;
    }
    return null;
  }
  
  const parent = findParentByDepth(newLayout, newChildren[0].depth);
  parentId = parent?.node.id ?? null;

  // Apply parent's current offset to new children
  if (parentId && prev.has(parentId)) {
    const parentOffset = prev.get(parentId)!;
    for (const child of newChildren) {
      next.set(child.node.id, parentOffset);
    }
  }

  const existing: Placed[] = [];
  function collect(p: Placed) {
    if (skipIds.has(p.node.id)) return;
    if (p.depth === childDepth) { existing.push(p); return; }
    if (p.depth < childDepth) p.children.forEach(collect);
  }
  collect(oldLayout);

  const movable = new Set(existing.map(e => e.node.id));
  sweepDown([...newChildren, ...existing], movable, next);

  return next;
}

// ─── SVG rendering ───────────────────────────────────────────────────────────

function renderEdges(p: Placed, offsets: Map<string, Offset>): React.ReactNode[] {
  const edges: React.ReactNode[] = [];
  const po = off(p.node.id, offsets);
  const px = p.x + po.dx + NW; const py = p.y + po.dy;
  for (const c of p.children) {
    const co = off(c.node.id, offsets);
    const cx = c.x + co.dx; const cy = c.y + co.dy;
    const mx = (px + cx) / 2;
    edges.push(
      <path key={`e-${c.node.id}`}
        d={`M${px},${py} C${mx},${py} ${mx},${cy} ${cx},${cy}`}
        stroke="#2a2a2a" strokeWidth={1.5} fill="none" />,
    );
    edges.push(...renderEdges(c, offsets));
  }
  return edges;
}

interface NodeOpts {
  expanded: Set<string>;
  openIds: Set<string>;
  offsets: Map<string, Offset>;
  onNodeClick: (node: MindmapNode) => void;
  onNodeMouseDown: (node: MindmapNode, e: React.MouseEvent) => void;
}

function renderNodes(p: Placed, opts: NodeOpts): React.ReactNode[] {
  const nodes: React.ReactNode[] = [];
  const col = palette(p.depth);
  const po = off(p.node.id, opts.offsets);
  const nx = p.x + po.dx; const ny = p.y + po.dy - NH / 2;
  const cy = ny + NH / 2;
  const hasChildren = p.node.children.length > 0;
  const isExpanded = opts.expanded.has(p.node.id);
  const isOpen = opts.openIds.has(p.node.id);

  nodes.push(
    <g key={`n-${p.node.id}`} style={{ cursor: "grab" }}
      onClick={(e) => { e.stopPropagation(); opts.onNodeClick(p.node); }}
      onMouseDown={(e) => { e.stopPropagation(); opts.onNodeMouseDown(p.node, e); }}
    >
      <rect x={nx} y={ny} width={NW} height={NH} rx={6} ry={6}
        fill={isOpen ? col.stroke : col.fill} stroke={col.stroke} strokeWidth={isOpen ? 2 : 1} />
      {hasChildren && (
        <text x={nx + NW - 10} y={cy + 4} fontSize={11}
          fill={isOpen ? col.fill : col.text}
          style={{ userSelect: "none", pointerEvents: "none" }}>
          {isExpanded ? "−" : "+"}
        </text>
      )}
      <foreignObject x={nx + 6} y={ny + 2} width={hasChildren ? NW - 22 : NW - 12} height={NH - 4}>
        {/* @ts-expect-error: xmlns required for SVG foreignObject */}
        <div xmlns="http://www.w3.org/1999/xhtml" style={{
          width: "100%", height: "100%",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: p.depth === 0 ? "12px" : "11px",
          fontWeight: p.depth === 0 ? 700 : 500,
          color: isOpen ? col.fill : col.text,
          textAlign: "center", lineHeight: 1.2,
          overflow: "hidden", fontFamily: "sans-serif", pointerEvents: "none",
        }}>
          {p.node.label}
        </div>
      </foreignObject>
    </g>,
  );

  for (const c of p.children) nodes.push(...renderNodes(c, opts));
  return nodes;
}

// ─── PNG download ─────────────────────────────────────────────────────────────

function downloadAsPng(
  root: MindmapNode, expanded: Set<string>, offsets: Map<string, Offset>, filename: string,
) {
  const layout = place(root, 0, 0, 0, expanded);
  const b = bounds(layout, offsets);
  const w = b.x2 - b.x1 + PAD * 2; const h = b.y2 - b.y1 + PAD * 2;
  const ox = PAD - b.x1; const oy = PAD - b.y1;
  const ns = "http://www.w3.org/2000/svg";

  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("width", String(w)); svg.setAttribute("height", String(h)); svg.setAttribute("xmlns", ns);
  const bg = document.createElementNS(ns, "rect");
  bg.setAttribute("width", String(w)); bg.setAttribute("height", String(h)); bg.setAttribute("fill", "#0d0d0d");
  svg.appendChild(bg);

  function appendEdges(p: Placed) {
    const po = off(p.node.id, offsets);
    const px = p.x + po.dx + ox + NW; const py = p.y + po.dy + oy;
    for (const c of p.children) {
      const co = off(c.node.id, offsets);
      const cx2 = c.x + co.dx + ox; const cy2 = c.y + co.dy + oy; const mx = (px + cx2) / 2;
      const path = document.createElementNS(ns, "path");
      path.setAttribute("d", `M${px},${py} C${mx},${py} ${mx},${cy2} ${cx2},${cy2}`);
      path.setAttribute("stroke", "#2a2a2a"); path.setAttribute("stroke-width", "1.5");
      path.setAttribute("fill", "none");
      svg.appendChild(path); appendEdges(c);
    }
  }

  function appendNodes(p: Placed) {
    const col = palette(p.depth);
    const po = off(p.node.id, offsets);
    const nx2 = p.x + po.dx + ox; const ny2 = p.y + po.dy + oy - NH / 2;
    const rect = document.createElementNS(ns, "rect");
    rect.setAttribute("x", String(nx2)); rect.setAttribute("y", String(ny2));
    rect.setAttribute("width", String(NW)); rect.setAttribute("height", String(NH));
    rect.setAttribute("rx", "6"); rect.setAttribute("fill", col.fill);
    rect.setAttribute("stroke", col.stroke); rect.setAttribute("stroke-width", "1");
    svg.appendChild(rect);
    const text = document.createElementNS(ns, "text");
    text.setAttribute("x", String(nx2 + NW / 2)); text.setAttribute("y", String(p.y + po.dy + oy + 4));
    text.setAttribute("text-anchor", "middle"); text.setAttribute("fill", col.text);
    text.setAttribute("font-size", p.depth === 0 ? "12" : "11");
    text.setAttribute("font-weight", p.depth === 0 ? "700" : "500");
    text.setAttribute("font-family", "sans-serif");
    text.textContent = p.node.label;
    svg.appendChild(text);
    for (const c of p.children) appendNodes(c);
  }

  appendEdges(layout); appendNodes(layout);
  const svgData = new XMLSerializer().serializeToString(svg);
  const blob = new Blob([svgData], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const img = new Image();
  img.onload = () => {
    const canvas = document.createElement("canvas");
    canvas.width = w; canvas.height = h;
    const ctx = canvas.getContext("2d")!;
    ctx.fillStyle = "#0d0d0d"; ctx.fillRect(0, 0, w, h);
    ctx.drawImage(img, 0, 0); URL.revokeObjectURL(url);
    const a = document.createElement("a");
    a.download = `${filename}.png`; a.href = canvas.toDataURL("image/png"); a.click();
  };
  img.src = url;
}

// ─── Component ────────────────────────────────────────────────────────────────

interface MindmapTreeProps {
  root: MindmapNode;
  filename?: string;
  downloadRef?: React.RefObject<(() => void) | null>;
}

export function MindmapTree({ root, filename = "mindmap", downloadRef }: MindmapTreeProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const layoutRef = useRef<Placed | null>(null);

  const [expanded, setExpanded] = useState<Set<string>>(() => new Set([root.id]));
  const [openNodes, setOpenNodes] = useState<MindmapNode[]>([]);
  const [nodeOffsets, setNodeOffsets] = useState<Map<string, Offset>>(() => new Map());
  const [vp, setVp] = useState<Viewport>({ zoom: 1, panX: 64, panY: CONTAINER_H / 2 });

  const dragState = useRef<DragState | null>(null);
  const didDrag = useRef(false);

  // Non-passive wheel — zoom toward cursor
  useEffect(() => {
    const el = svgRef.current;
    if (!el) return;
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const rect = el.getBoundingClientRect();
      const cx = e.clientX - rect.left; const cy = e.clientY - rect.top;
      setVp((v) => {
        const factor = e.deltaY < 0 ? 1.05 : 0.95;
        const newZoom = Math.max(0.2, Math.min(3, v.zoom * factor));
        const ratio = newZoom / v.zoom;
        return { zoom: newZoom, panX: cx + (v.panX - cx) * ratio, panY: cy + (v.panY - cy) * ratio };
      });
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, []);

  // Prevent context menu on right-click
  useEffect(() => {
    const el = svgRef.current;
    if (!el) return;
    const onContextMenu = (e: MouseEvent) => {
      e.preventDefault();
    };
    el.addEventListener("contextmenu", onContextMenu);
    return () => el.removeEventListener("contextmenu", onContextMenu);
  }, []);

  function handleNodeMouseDown(node: MindmapNode, e: React.MouseEvent) {
    e.preventDefault();
    const placed = layoutRef.current ? findPlaced(layoutRef.current, node.id) : null;
    
    // Determine which nodes to drag based on mouse button
    let nodeIds: string[];
    if (e.button === 2 && placed) {
      // Right-click: move parent and all its children
      nodeIds = collectSubtreeIds(placed);
    } else if (e.button === 0) {
      // Left-click: move only the individual node
      nodeIds = [node.id];
    } else {
      // Other buttons: ignore
      return;
    }
    
    const startOffsets = new Map<string, Offset>(
      nodeIds.map((id) => [id, nodeOffsets.get(id) ?? { dx: 0, dy: 0 }]),
    );
    dragState.current = { type: "node", nodeIds, startX: e.clientX, startY: e.clientY, startOffsets };
    didDrag.current = false;
  }

  function handleSvgMouseDown(e: React.MouseEvent) {
    if (e.button !== 0) return;
    dragState.current = { type: "canvas", startX: e.clientX, startY: e.clientY, startPanX: vp.panX, startPanY: vp.panY };
    didDrag.current = false;
  }

  function handleMouseMove(e: React.MouseEvent) {
    const ds = dragState.current;
    if (!ds) return;
    if (ds.type === "canvas") {
      const dx = e.clientX - ds.startX; const dy = e.clientY - ds.startY;
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) didDrag.current = true;
      setVp((v) => ({ ...v, panX: ds.startPanX + dx, panY: ds.startPanY + dy }));
    } else {
      const sdx = (e.clientX - ds.startX) / vp.zoom;
      const sdy = (e.clientY - ds.startY) / vp.zoom;
      if (Math.abs(sdx) > 3 || Math.abs(sdy) > 3) didDrag.current = true;
      setNodeOffsets((prev) => {
        const next = new Map(prev);
        for (const id of ds.nodeIds) {
          const so = ds.startOffsets.get(id) ?? { dx: 0, dy: 0 };
          next.set(id, { dx: so.dx + sdx, dy: so.dy + sdy });
        }
        return next;
      });
    }
  }

  function handleMouseUp() { dragState.current = null; }

  function handleNodeClick(node: MindmapNode) {
    if (didDrag.current) return;
    const alreadyOpen = openNodes.some((n) => n.id === node.id);
    if (alreadyOpen) {
      if (node.children.length > 0) {
        setExpanded((prev) => {
          const next = new Set(prev);
          if (next.has(node.id)) next.delete(node.id); else next.add(node.id);
          return next;
        });
      }
    } else {
      const currentLayout = layoutRef.current ?? place(root, 0, 0, 0, expanded);
      const newExpanded = new Set(expanded);
      if (node.children.length > 0) newExpanded.add(node.id);
      const newLayout = place(root, 0, 0, 0, newExpanded);
      const placed = findPlaced(newLayout, node.id);

      setNodeOffsets((prev) => {
        let next = prev;
        // Push siblings below to make room for the description
        if (placed) {
          const descH = estimateDescH(node.label, node.description ?? "");
          next = applyDescriptionShift(next, newLayout, placed, descH);
        }
        // Push existing nodes that would overlap with new children
        if (placed && placed.children.length > 0) {
          const skipIds = new Set(placed.children.map((c) => c.node.id));
          next = applyExpansionShift(next, currentLayout, placed.children, skipIds, newLayout);
        }
        return next;
      });

      setExpanded(newExpanded);
      setOpenNodes((prev) => [...prev, node]);
    }
  }

  function closeDescription(nodeId: string) {
    setOpenNodes((prev) => prev.filter((n) => n.id !== nodeId));
  }

  if (downloadRef) {
    (downloadRef as React.MutableRefObject<(() => void) | null>).current =
      () => downloadAsPng(root, expanded, nodeOffsets, filename);
  }

  const layout = place(root, 0, 0, 0, expanded);
  layoutRef.current = layout;
  const openIds = new Set(openNodes.map((n) => n.id));

  return (
    <svg
      ref={svgRef}
      width="100%"
      height={CONTAINER_H}
      style={{ background: "#0d0d0d", borderRadius: 8, display: "block", cursor: "grab", userSelect: "none" }}
      onMouseDown={handleSvgMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <g transform={`translate(${vp.panX},${vp.panY}) scale(${vp.zoom})`}>
        {renderEdges(layout, nodeOffsets)}
        {renderNodes(layout, {
          expanded, openIds, offsets: nodeOffsets,
          onNodeClick: handleNodeClick,
          onNodeMouseDown: handleNodeMouseDown,
        })}

        {/* Description panels — follow each node's current position */}
        {openNodes.map((node) => {
          const placed = findPlaced(layout, node.id);
          if (!placed) return null;
          const po = off(node.id, nodeOffsets);
          const nx = placed.x + po.dx;
          const ny = placed.y + po.dy;
          const h = estimateDescH(node.label, node.description ?? "");
          return (
            <foreignObject
              key={node.id}
              x={nx + NW / 2 - DESC_W / 2}
              y={ny + NH / 2 + DESC_GAP}
              width={DESC_W}
              height={h}
              onClick={(e) => e.stopPropagation()}
              onMouseDown={(e) => { e.stopPropagation(); handleNodeMouseDown(node, e); }}
            >
              {/* @ts-expect-error: xmlns required for SVG foreignObject */}
              <div xmlns="http://www.w3.org/1999/xhtml" style={{
                position: "relative",
                background: "#1a1a1a", border: "1px solid #2e2e2e", borderRadius: 8,
                padding: "8px 26px 8px 10px",
                width: "100%", boxSizing: "border-box", fontFamily: "sans-serif",
                cursor: "grab",
              }}>
                <button
                  onClick={() => closeDescription(node.id)}
                  onMouseDown={(e) => e.stopPropagation()}
                  style={{
                    position: "absolute", top: 5, right: 5,
                    background: "transparent", border: "none",
                    color: "#6b7280", cursor: "pointer", fontSize: 13, lineHeight: 1, padding: "2px 3px",
                  }}
                >×</button>
                <p style={{ fontSize: 11, fontWeight: 700, color: "#e0e0e0", margin: "0 0 4px 0" }}>
                  {node.label}
                </p>
                <p style={{ fontSize: 10, color: "#9ca3af", lineHeight: 1.65, margin: 0 }}>
                  {node.description || "No description available."}
                </p>
              </div>
            </foreignObject>
          );
        })}
      </g>

      {/* Hint — fixed at bottom, outside pan/zoom transform */}
      <text x="50%" y={CONTAINER_H - 9} textAnchor="middle" fontSize={12} fill="#FFFFFF"
        style={{ userSelect: "none", pointerEvents: "none" }}>
        Click node to reveal description · Drag nodes to rearrange (Right-click to move with child nodes) · Scroll to zoom · Drag canvas to pan
      </text>
    </svg>
  );
}
