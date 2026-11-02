"use client";

import { useMemo, useState } from "react";

type Room = {
  room_number: string;
  floor: number;
  room_type: string;
  room_type_name: string;
  king_beds: number;
  queen_beds: number;
  sofa_bed: boolean;
  view: string;
  accessible: boolean;
  suite: boolean;
  skylight: boolean;
  housekeeping_status: string;
  maintenance_status: string;
};

export default function RoomFilters({ rooms }: { rooms: Room[] }) {
  const [floor, setFloor] = useState("all");
  const [category, setCategory] = useState("all");

  const floors = useMemo(
    () => [...new Set(rooms.map((room) => room.floor))].sort((a, b) => a - b),
    [rooms]
  );

  const categories = useMemo(
    () => [...new Set(rooms.map((room) => room.room_type))].sort(),
    [rooms]
  );

  const filtered = rooms.filter(
    (room) =>
      (floor === "all" || room.floor === Number(floor)) &&
      (category === "all" || room.room_type === category)
  );

  return (
    <>
      <div className="flex flex-wrap items-end gap-4 border-b border-[#d9e2ec] p-5">
        <div>
          <label htmlFor="floor-filter" className="mb-1 block text-xs font-semibold">
            Floor
          </label>
          <select
            id="floor-filter"
            value={floor}
            onChange={(event) => setFloor(event.target.value)}
            className="rounded border border-slate-300 bg-white px-4 py-2 text-sm"
          >
            <option value="all">All Floors</option>
            {floors.map((value) => (
              <option key={value} value={value}>
                Floor {value}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="type-filter" className="mb-1 block text-xs font-semibold">
            Room Category
          </label>
          <select
            id="type-filter"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            className="rounded border border-slate-300 bg-white px-4 py-2 text-sm"
          >
            <option value="all">All Categories</option>
            {categories.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </div>

        <button
          type="button"
          onClick={() => {
            setFloor("all");
            setCategory("all");
          }}
          className="rounded border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-100"
        >
          Reset Filters
        </button>

        <span className="pb-2 text-xs text-slate-500">
          Showing {filtered.length} of {rooms.length} imported rooms
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[1200px] text-left text-sm">
          <thead className="bg-[#eaf0f7] text-xs uppercase text-[#52677f]">
            <tr>
              {["Room", "Floor", "Category", "Description", "Beds", "View", "Features", "Housekeeping", "Maintenance"].map(
                (heading) => (
                  <th key={heading} className="px-5 py-4">
                    {heading}
                  </th>
                )
              )}
            </tr>
          </thead>
          <tbody>
            {filtered.map((room, index) => (
              <tr
                key={room.room_number}
                className={`border-t border-[#edf0f4] ${
                  index % 2 ? "bg-[#f9fbfd]" : "bg-white"
                }`}
              >
                <td className="px-5 py-4 font-semibold text-blue-700">
                  {room.room_number}
                </td>
                <td className="px-5 py-4">{room.floor}</td>
                <td className="px-5 py-4 font-semibold">{room.room_type}</td>
                <td className="px-5 py-4">{room.room_type_name}</td>
                <td className="px-5 py-4">
                  {[
                    room.king_beds > 0 ? `${room.king_beds} King` : "",
                    room.queen_beds > 0 ? `${room.queen_beds} Queen` : "",
                  ].filter(Boolean).join(" + ")}
                  {room.sofa_bed && (
                    <div className="text-xs text-blue-700">Sofa Bed</div>
                  )}
                </td>
                <td className="px-5 py-4 capitalize">
                  {room.view === "not_specified" ? "—" : room.view}
                </td>
                <td className="px-5 py-4">
                  {[
                    room.accessible ? "Accessible" : "",
                    room.suite ? "Suite" : "",
                    room.skylight ? "Skylight" : "",
                  ].filter(Boolean).join(", ") || "—"}
                </td>
                <td className="px-5 py-4">
                  <span className="rounded bg-slate-100 px-3 py-1 text-xs text-slate-600">
                    {room.housekeeping_status}
                  </span>
                </td>
                <td className="px-5 py-4">
                  <span className="rounded bg-slate-100 px-3 py-1 text-xs text-slate-600">
                    {room.maintenance_status}
                  </span>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={9} className="p-8 text-center text-slate-500">
                  No rooms match these filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}

