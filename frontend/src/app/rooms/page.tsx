import RoomFilters from "./RoomFilters";
import Link from "next/link";
import { Suspense } from "react";

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

type RoomResponse = {
  rooms: Room[];
  total: number;
  hotel_capacity: number;
  inventory_complete: boolean;
};

async function RoomWorkspace() {
  let data: RoomResponse | null = null;

  try {
    const response = await fetch("http://127.0.0.1:8000/api/rooms", {
      cache: "no-store",
    });

    if (!response.ok) throw new Error("Room API unavailable");

    data = await response.json();
  } catch {
    // Show an offline message below.
  }

  const rooms = data?.rooms ?? [];
  const floors = [...new Set(rooms.map((r) => r.floor))].sort();
  const categories = [...new Set(rooms.map((r) => r.room_type))].sort();

  return (
    <div className="min-h-screen bg-[#f2f5f9] text-[#243247]">
      <header className="bg-[#123d70] px-6 py-5 text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xl font-bold">StayPilot AI</div>
            <div className="text-xs text-blue-200">PROPERTY MANAGEMENT SYSTEM</div>
          </div>
          <div className="text-sm">Demo Property · 290 Rooms</div>
        </div>
      </header>

      <nav className="flex gap-6 border-b border-[#cbd7e5] bg-white px-6 text-sm">
        <Link href="/" className="py-4 text-slate-500">
          Dashboard
        </Link>
        <Link
          href="/rooms"
          className="border-b-[3px] border-blue-600 py-4 font-semibold text-blue-700"
        >
          Room Management
        </Link>
      </nav>

      <main className="mx-auto max-w-[1500px] px-6 py-8">
        <div className="mb-6">
          <div className="text-xs text-slate-500">
            Home / Hotel Operations / Room Management
          </div>
          <h1 className="mt-2 text-2xl font-semibold text-[#17385c]">
            Room Management
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Room inventory, housekeeping, and maintenance overview
          </p>
        </div>

        <div className="mb-6 grid gap-4 sm:grid-cols-3">
          {[
            ["Hotel Capacity", data?.hotel_capacity ?? "—"],
            ["Imported Rooms", data?.total ?? "—"],
            ["Unmapped Rooms", data ? data.hotel_capacity - data.total : "—"],
          ].map(([label, value]) => (
            <div key={label} className="border border-[#d9e2ec] bg-white p-5 shadow-sm">
              <div className="text-xs font-semibold uppercase text-slate-500">
                {label}
              </div>
              <div className="mt-2 text-3xl font-semibold text-[#17385c]">
                {value}
              </div>
            </div>
          ))}
        </div>

        {!data && (
          <div className="mb-6 border border-red-200 bg-red-50 p-4 text-red-700">
            Unable to connect to the room inventory API.
          </div>
        )}

        <section className="border border-[#d9e2ec] bg-white shadow-sm">
          <div className="border-b border-[#d9e2ec] bg-[#f8fafc] px-5 py-4">
            <h2 className="font-semibold text-[#17385c]">Room Rack</h2>
            <p className="mt-1 text-xs text-slate-500">
              Complete 290-room inventory · Housekeeping status not yet available
            </p>
          </div>

          <RoomFilters rooms={rooms} />
        </section>

        <p className="mt-5 text-xs text-slate-500">
          Development environment · Complete room mapping · No live room availability calculations
        </p>
      </main>
    </div>
  );
}

export default function RoomsPage() {
  return (
    <Suspense fallback={<div className="p-10">Loading room management...</div>}>
      <RoomWorkspace />
    </Suspense>
  );
}



