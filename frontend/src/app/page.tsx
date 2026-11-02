import { Suspense } from "react";

type Dashboard = {
  date: string;
  total_reservations: number;
  arrivals_today: number;
  departures_today: number;
  occupied_rooms: number;
};

type Reservation = {
  id: string;
  guest_name: string;
  room_number: string;
  room_type: string;
  arrival_date: string;
  departure_date: string;
  status: string;
};

async function getData<T>(path: string): Promise<T> {
  const response = await fetch(`http://127.0.0.1:8000${path}`, {
    cache: "no-store",
  });

  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
}

const navigation = [
  "Dashboard",
  "Reservations",
  "Front Desk",
  "Room Management",
  "Guest Profiles",
  "Reports",
];

async function OperationsWorkspace() {
  let dashboard: Dashboard | null = null;
  let reservations: Reservation[] = [];

  try {
    const [stats, records] = await Promise.all([
      getData<Dashboard>("/api/dashboard"),
      getData<{ reservations: Reservation[] }>("/api/reservations"),
    ]);
    dashboard = stats;
    reservations = records.reservations;
  } catch {
    // The interface displays a connection warning below.
  }

  const today = dashboard?.date ?? "Unavailable";

  const arrivals = reservations.filter(
    (r) => r.arrival_date === today && r.status === "reserved"
  );
  const departures = reservations.filter(
    (r) => r.departure_date === today && r.status === "checked_in"
  );

  const stats = [
    { label: "Arrivals Today", value: dashboard?.arrivals_today ?? "—", color: "border-blue-600" },
    { label: "Departures Today", value: dashboard?.departures_today ?? "—", color: "border-amber-500" },
    { label: "In-House Rooms", value: dashboard?.occupied_rooms ?? "—", color: "border-emerald-600" },
    { label: "Reservations", value: dashboard?.total_reservations ?? "—", color: "border-slate-500" },
  ];

  return (
    <div className="min-h-screen bg-[#f2f5f9] text-[#243247]">
      <header className="bg-[#123d70] text-white shadow-sm">
        <div className="flex min-h-16 items-center justify-between gap-4 px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded bg-white/15 text-lg font-bold">
              S
            </div>
            <div>
              <div className="text-lg font-bold tracking-tight">StayPilot AI</div>
              <div className="text-[10px] uppercase tracking-[0.15em] text-blue-200">
                Property Management System
              </div>
            </div>
          </div>

          <div className="hidden items-center gap-5 text-xs md:flex">
            <span className="rounded border border-white/25 bg-white/10 px-3 py-2">
              Demo Property ▾
            </span>
            <span>Business Date: {today}</span>
            <span className="rounded-full bg-white/15 px-3 py-2">Front Desk</span>
          </div>
        </div>
      </header>

      <nav className="border-b border-[#cbd7e5] bg-white">
        <div className="flex overflow-x-auto px-6">
          {navigation.map((item, index) => (
            <div
              key={item}
              className={`shrink-0 border-b-[3px] px-5 py-4 text-sm font-medium ${
                index === 0
                  ? "border-[#1477c9] bg-[#edf5fc] text-[#125b99]"
                  : "border-transparent text-[#53667b]"
              }`}
            >
              {item}
            </div>
          ))}
        </div>
      </nav>

      <main className="mx-auto max-w-[1500px] px-6 py-7">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="mb-1 text-xs text-[#708198]">
              Home / Hotel Operations / Dashboard
            </div>
            <h1 className="text-2xl font-semibold text-[#17385c]">
              Front Desk Dashboard
            </h1>
            <p className="mt-1 text-sm text-[#6b7c91]">
              Daily property operations and guest movement
            </p>
          </div>
          <div className="flex gap-2">
            <span className={`rounded border px-3 py-2 text-xs font-semibold ${
              dashboard
                ? "border-green-200 bg-green-50 text-green-700"
                : "border-red-200 bg-red-50 text-red-700"
            }`}>
              {dashboard ? "● System Connected" : "● Backend Offline"}
            </span>
            <span className="rounded border border-[#cbd7e5] bg-white px-4 py-2 text-xs font-semibold">
              Business Date: {today}
            </span>
          </div>
        </div>

        <div className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className={`border border-[#d9e2ec] border-l-4 ${stat.color} bg-white p-5 shadow-sm`}
            >
              <div className="text-xs font-semibold uppercase tracking-wide text-[#718298]">
                {stat.label}
              </div>
              <div className="mt-3 text-3xl font-semibold text-[#17385c]">
                {stat.value}
              </div>
              <div className="mt-2 text-xs text-[#8390a2]">
                Current operational count
              </div>
            </div>
          ))}
        </div>

        <div className="mb-6 grid gap-5 lg:grid-cols-2">
          <section className="border border-[#d9e2ec] bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-[#e2e8f0] bg-[#f8fafc] px-5 py-4">
              <h2 className="font-semibold text-[#17385c]">Expected Arrivals</h2>
              <span className="rounded bg-blue-100 px-2 py-1 text-xs font-semibold text-blue-700">
                {arrivals.length} Arrivals
              </span>
            </div>
            <div className="divide-y divide-[#edf0f4]">
              {arrivals.map((r) => (
                <div key={r.id} className="flex items-center justify-between gap-3 px-5 py-4 text-sm">
                  <div>
                    <div className="font-semibold">{r.guest_name}</div>
                    <div className="mt-1 text-xs text-[#7a8a9d]">{r.id} · {r.room_type}</div>
                  </div>
                  <span className="text-xs font-medium text-blue-700">Room {r.room_number}</span>
                </div>
              ))}
              {arrivals.length === 0 && <p className="p-5 text-sm text-slate-500">No expected arrivals.</p>}
            </div>
          </section>

          <section className="border border-[#d9e2ec] bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-[#e2e8f0] bg-[#f8fafc] px-5 py-4">
              <h2 className="font-semibold text-[#17385c]">Expected Departures</h2>
              <span className="rounded bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-800">
                {departures.length} Departures
              </span>
            </div>
            <div className="divide-y divide-[#edf0f4]">
              {departures.map((r) => (
                <div key={r.id} className="flex items-center justify-between gap-3 px-5 py-4 text-sm">
                  <div>
                    <div className="font-semibold">{r.guest_name}</div>
                    <div className="mt-1 text-xs text-[#7a8a9d]">{r.id} · {r.room_type}</div>
                  </div>
                  <span className="text-xs font-medium text-amber-700">Room {r.room_number}</span>
                </div>
              ))}
              {departures.length === 0 && <p className="p-5 text-sm text-slate-500">No expected departures.</p>}
            </div>
          </section>
        </div>

        <section className="border border-[#d9e2ec] bg-white shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#d9e2ec] px-5 py-4">
            <div>
              <h2 className="font-semibold text-[#17385c]">Reservation Management</h2>
              <p className="mt-1 text-xs text-[#8390a2]">
                Active reservations and in-house guests · Demo data
              </p>
            </div>
            <span className="rounded bg-[#edf5fc] px-3 py-2 text-xs font-semibold text-[#125b99]">
              {reservations.length} Records
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[850px] text-left text-sm">
              <thead className="border-b border-[#d9e2ec] bg-[#eaf0f7] text-xs uppercase text-[#52677f]">
                <tr>
                  {["Confirmation", "Guest Name", "Room", "Room Type", "Arrival", "Departure", "Status"].map((h) => (
                    <th key={h} className="px-5 py-3 font-semibold">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {reservations.map((r, i) => (
                  <tr key={r.id} className={`border-b border-[#edf0f4] ${i % 2 ? "bg-[#f9fbfd]" : "bg-white"}`}>
                    <td className="px-5 py-3 font-semibold text-[#146cae]">{r.id}</td>
                    <td className="px-5 py-3 font-medium">{r.guest_name}</td>
                    <td className="px-5 py-3">{r.room_number}</td>
                    <td className="px-5 py-3">{r.room_type}</td>
                    <td className="px-5 py-3">{r.arrival_date}</td>
                    <td className="px-5 py-3">{r.departure_date}</td>
                    <td className="px-5 py-3">
                      <span className={`rounded px-2 py-1 text-xs font-semibold ${
                        r.status === "checked_in"
                          ? "bg-green-100 text-green-800"
                          : "bg-blue-100 text-blue-800"
                      }`}>
                        {r.status === "checked_in" ? "IN HOUSE" : "RESERVED"}
                      </span>
                    </td>
                  </tr>
                ))}
                {reservations.length === 0 && (
                  <tr><td colSpan={7} className="p-8 text-center text-slate-500">No reservations available.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <footer className="mt-6 flex flex-wrap items-center justify-between gap-2 text-xs text-[#8a98a9]">
          <span>StayPilot AI · Hotel Operations Platform</span>
          <span>Development Environment · Synthetic Guest Data</span>
        </footer>
      </main>
    </div>
  );
}

export default function Home() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen bg-[#f2f5f9] p-10 text-[#17385c]">
          Loading StayPilot AI hotel operations...
        </main>
      }
    >
      <OperationsWorkspace />
    </Suspense>
  );
}
