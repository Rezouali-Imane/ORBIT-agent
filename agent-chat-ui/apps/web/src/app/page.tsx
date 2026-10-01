"use client";

import { Thread } from "@/components/thread";
import { StreamProvider } from "@/providers/Stream";
import { ThreadProvider } from "@/providers/Thread";
import { Toaster } from "@/components/ui/sonner";
import { BookOpen, Check, FileText, GitBranch, Globe2, Search, ShieldCheck, UserRound } from "lucide-react";
import React, { useEffect, useState } from "react";
import { useQueryState } from "nuqs";

const specialists = [
  { name: "Manager", icon: UserRound, copy: "Reads your question and decides who should work on it.", tone: "green" },
  { name: "Librarian", icon: BookOpen, copy: "Answers from your own documents and cites the page.", tone: "terracotta" },
  { name: "Researcher", icon: Globe2, copy: "Searches the web for current information and links to it.", tone: "ochre" },
  { name: "Checker", icon: ShieldCheck, copy: "Flags any claim without a source before you see the answer.", tone: "blue" },
];

const previewSpecialists = [
  { name: "Manager", icon: UserRound, state: "" },
  { name: "Librarian", icon: BookOpen, state: "is-active" },
  { name: "Researcher", icon: Search, state: "" },
  { name: "Checker", icon: Check, state: "" },
];

function ServerStatus() {
  const [apiUrl] = useQueryState("apiUrl");
  const [status, setStatus] = useState<"checking" | "online" | "offline">("checking");
  const endpoint = apiUrl || process.env.NEXT_PUBLIC_API_URL || "http://localhost:2024";

  useEffect(() => {
    let active = true;
    fetch(`${endpoint}/info`)
      .then((response) => { if (active) setStatus(response.ok ? "online" : "offline"); })
      .catch(() => { if (active) setStatus("offline"); });
    return () => { active = false; };
  }, [endpoint]);

  return <span className={`orbit-status orbit-status--${status}`}><i /> {status === "checking" ? "Checking" : status}</span>;
}

function OrbitLogo({ small = false }: { small?: boolean }) {
  return <img className={small ? "orbit-logo orbit-logo--small" : "orbit-logo"} src="/images-removebg-preview.svg" alt="" />;
}

function ProductPreview() {
  return (
    <div className="orbit-preview" aria-label="Example Orbit answer from a document">
      <div className="orbit-preview__bar"><span className="orbit-preview__label"><i /> Example workspace</span><span className="orbit-preview__dots"><i /><i /><i /></span></div>
      <div className="orbit-preview__body">
        <div className="orbit-preview__question"><span>You</span><p>What does our handbook say about launch reviews?</p></div>
        <div className="orbit-preview__answer"><div className="orbit-preview__avatar"><OrbitLogo small /></div><div><span className="orbit-preview__label">Orbit</span><p>The handbook recommends a launch review before release. The review covers readiness, ownership, and rollback plans.</p><a href="#team-section"><FileText size={13} /> Source: handbook.pdf, p. 4</a></div></div>
        <div className="orbit-preview__specialists"><span>Worked on this</span>{previewSpecialists.map(({ name, icon: Icon, state }) => <span className={state} key={name}><Icon size={13} /> {name}</span>)}</div>
      </div>
    </div>
  );
}

function OrbitLanding({ onContinue }: { onContinue: () => void }) {
  return (
    <main className="orbit-landing">
      <header className="orbit-header">
        <a className="orbit-brand" href="#top" aria-label="Orbit home"><span className="orbit-brand__mark"><OrbitLogo small /></span><span>Orbit</span></a>
        <ServerStatus />
      </header>

      <section className="orbit-hero" id="top">
        <div className="orbit-hero__copy"><p className="orbit-kicker">A team of specialists for your questions</p><h1>Ask Orbit.<br />Get answers you can check.</h1><p className="orbit-hero__subtext">Orbit reads your documents, searches the web, and checks its own work before it replies. Every answer shows its sources, and nothing is saved until you approve it.</p><div className="orbit-hero__actions"><button className="orbit-button orbit-button--primary" onClick={onContinue}>Open workspace <span>↗</span></button><a className="orbit-button orbit-button--secondary" href="#team-section">See how it works <span>↓</span></a></div></div>
        <ProductPreview />
      </section>

      <section className="orbit-section" id="team-section"><div className="orbit-section__heading"><p className="orbit-kicker">The team</p><h2>Who does what</h2></div><div className="orbit-card-grid">{specialists.map(({ name, icon: Icon, copy, tone }) => <article className="orbit-info-card" key={name}><span className={`orbit-info-card__icon orbit-info-card__icon--${tone}`}><Icon size={17} /></span><h3>{name}</h3><p>{copy}</p></article>)}</div></section>

      <section className="orbit-section orbit-section--tools"><div className="orbit-section__heading"><p className="orbit-kicker">Built into the workspace</p><h2>What Orbit can do for you</h2></div><div className="orbit-tool-grid"><article className="orbit-tool-card"><FileText size={19} /><div><h3>Notes</h3><p>Orbit can save project notes for you. It shows you the note first, and saves it only after you approve.</p></div></article><article className="orbit-tool-card"><GitBranch size={19} /><div><h3>Roadmap</h3><p>Turns a plan into a structured roadmap you can follow.</p></div></article></div></section>

      <section className="orbit-section orbit-section--control"><div className="orbit-section__heading"><p className="orbit-kicker">A clear boundary</p><h2>You stay in control</h2></div><div className="orbit-control-list"><p><Check size={17} /> Sources on every answer.</p><p><Check size={17} /> Approval before anything is saved.</p><p><Check size={17} /> Web pages and documents are treated as information, never as instructions.</p></div></section>

      <footer className="orbit-footer"><span>Orbit · Built for answers you can check.</span><a href="https://github.com/Rezouali-Imane" target="_blank" rel="noreferrer">GitHub ↗</a></footer>
    </main>
  );
}

export default function DemoPage(): React.ReactNode {
  const [showWorkspace, setShowWorkspace] = useState(false);

  return (
    <React.Suspense fallback={<div>Loading (layout)...</div>}>
      <Toaster />
      <ThreadProvider>
        <StreamProvider>
          {showWorkspace ? <Thread /> : <OrbitLanding onContinue={() => setShowWorkspace(true)} />}
        </StreamProvider>
      </ThreadProvider>
    </React.Suspense>
  );
}
