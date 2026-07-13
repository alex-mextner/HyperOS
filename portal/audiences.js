// Four-audience front door for the Agent OS portal.
// Audiences: OS builders · third-party developers · investors · early users.
// Visual language derived from the engineering spec's layered system map and entity graph.
function audienceHome(){
  nav('home');
  app.innerHTML = `
  <section class="afront">
    <div class="afront-hero">
      <div class="afront-eyebrow">Fuchsia/Zircon fork · Rust-first · local-first · agent-native</div>
      <h1 class="afront-title">One operating system.<br><span class="afront-accent">Four ways in.</span></h1>
      <p class="afront-lede">Agent OS forks the entire Fuchsia tree and builds an entity-and-agent product layer on top — where documents, tasks, people, places and events are first-class system objects, not data trapped inside apps. Choose your path below.</p>
    </div>

    <div class="afront-grid">
      <a class="alane alane-build" href="#build">
        <div class="alane-num">01</div>
        <div class="alane-role">Build the OS</div>
        <h2>Engineers on Agent OS</h2>
        <p>Kernel fork, driver framework, layer manifests, the capability model, the demo-brick hardware, and the full engineering bible with evidence gates.</p>
        <div class="alane-cta">Enter the workspace →</div>
      </a>
      <a class="alane alane-dev" href="#developers">
        <div class="alane-num">02</div>
        <div class="alane-role">Build on Agent OS</div>
        <h2>Third-party developers</h2>
        <p>The entity/action contract, capability-scoped agents, typed actions with receipts, and how native clients reach services lawfully — the surface you build against.</p>
        <div class="alane-cta">Read the platform →</div>
      </a>
      <a class="alane alane-invest" href="#investors">
        <div class="alane-num">03</div>
        <div class="alane-role">Back the thesis</div>
        <h2>Investors</h2>
        <p>The wedge, the two-track strategy that de-risks hardware, the subscription-compute model, honest ceilings, and what evidence exists today versus what is planned.</p>
        <div class="alane-cta">See the case →</div>
      </a>
      <a class="alane alane-user" href="#users">
        <div class="alane-num">04</div>
        <div class="alane-role">Use it first</div>
        <h2>Early users</h2>
        <p>What the phone actually does: a voice agent you can inspect, instant single-purpose modes, days of standby, and privacy you can verify — not a slogan.</p>
        <div class="alane-cta">What you get →</div>
      </a>
    </div>

    <div class="afront-foot">
      <span>Shared foundation:</span>
      <a href="#wiki">Engineering bible</a>
      <a href="#tasks">Tasks</a>
      <a href="#gantt">Roadmap</a>
      <a href="#compare">iOS / Android / Agent OS</a>
      <a href="#landscape">OS landscape</a>
    </div>
  </section>`;
}

function buildLane(){
  nav('build');
  app.innerHTML = `
  <section class="lane-page">
    <div class="lane-head lane-head-build">
      <div class="lane-eyebrow">01 · Engineers on Agent OS</div>
      <h1>Build the operating system.</h1>
      <p class="lane-lede">We fork the entire Fuchsia tree — Zircon, DFv2, FIDL, Magma, Scenic/Flatland, Starnix, and the build system — and write board drivers plus the Rust-first product layer on top. Two tracks run in parallel: the product in emulation now, hardware bring-up separately.</p>
    </div>

    <div class="lane-layers">
      <h2 class="lane-h2">The layered system</h2>
      <div class="layerstack">
        <div class="lyr lyr6"><span class="lyr-id">L6</span><span class="lyr-name">Product · shell, entities, agents, history</span><span class="lyr-st st-new">from scratch</span></div>
        <div class="lyr lyr5"><span class="lyr-id">L5</span><span class="lyr-name">Compatibility · Starnix (Linux/Android userspace)</span><span class="lyr-st st-asis">as-is</span></div>
        <div class="lyr lyr4"><span class="lyr-id">L4</span><span class="lyr-name">Camera · capture + HDR+ + tuning</span><span class="lyr-st st-mix">wrap / tune</span></div>
        <div class="lyr lyr3"><span class="lyr-id">L3</span><span class="lyr-name">Telephony · pre-certified module (demo brick)</span><span class="lyr-st st-asis">as-is</span></div>
        <div class="lyr lyr2"><span class="lyr-id">L2</span><span class="lyr-name">GPU · Magma driver</span><span class="lyr-st st-port">port</span></div>
        <div class="lyr lyr1"><span class="lyr-id">L1</span><span class="lyr-name">Board bring-up · drivers, power island</span><span class="lyr-st st-port">port</span></div>
        <div class="lyr lyr0"><span class="lyr-id">L0</span><span class="lyr-name">Fuchsia fork · Zircon, DFv2, FIDL, Magma</span><span class="lyr-st st-fork">fork</span></div>
      </div>
      <p class="lane-note">Status legend mirrors the reuse taxonomy: <b>fork</b> the tree, take frameworks <b>as-is</b>, <b>port</b> driver knowledge, write the product <b>from scratch</b>. Most demo-brick hardware is as-is (pre-certified modules) — almost no reverse-engineering, which is why it ships years before a custom device.</p>
    </div>

    <div class="lane-cards">
      <a class="lcard" href="#wiki">→ Full engineering bible (151 documents)</a>
      <a class="lcard" href="${gh('/blob/main/engineering-bible/docs/decisions/AOS-ADR-0001.md')}">→ ADR-0001 · Fork Fuchsia/Zircon</a>
      <a class="lcard" href="${gh('/blob/main/engineering-bible/docs/architecture/ARCH-022-layer-manifest-and-capabilities.md')}">→ Capability model & layer manifests</a>
      <a class="lcard" href="${gh('/blob/main/engineering-bible/docs/hardware/HW-018-demo-brick-v1-configuration.md')}">→ Demo-brick V1 configuration</a>
      <a class="lcard" href="${gh('/blob/main/engineering-bible/docs/hardware/HW-019-power-architecture-standby.md')}">→ Power architecture & standby</a>
      <a class="lcard" href="#tasks">→ Live tasks & evidence gates</a>
    </div>
    <a class="lane-back" href="#home">← All audiences</a>
  </section>`;
}

function developersLane(){
  nav('developers');
  app.innerHTML = `
  <section class="lane-page">
    <div class="lane-head lane-head-dev">
      <div class="lane-eyebrow">02 · Third-party developers</div>
      <h1>Build on the object graph, not inside a silo.</h1>
      <p class="lane-lede">Apps become replaceable providers and views over one typed system. You publish typed actions and data sources; the OS gives them semantic history, capability-scoped access, and inspectable agent plans — for free.</p>
    </div>
    <div class="lane-two">
      <div class="ltile"><h3>Entity & action contract</h3><p>Register a data source or a typed action over shared entities (person, project, document, event, message). No private state path; everything is contract-first.</p></div>
      <div class="ltile"><h3>Capability-scoped agents</h3><p>Agents get exactly the authority you grant — least privilege by construction, revocable, and every effectful action leaves a receipt with an undo path.</p></div>
      <div class="ltile"><h3>Lawful service integration</h3><p>Reach services by the highest lawful method: official APIs, regulated interfaces (open banking), interop standards. Never defeat pinning or anti-tamper on others' apps.</p></div>
      <div class="ltile"><h3>Native clients, full features</h3><p>A native client gets entities, IntentBox actions, history, capabilities, instant-mode participation, offline, and agent access — or it isn't native.</p></div>
    </div>
    <div class="lane-cards">
      <a class="lcard" href="${gh('/blob/main/engineering-bible/docs/product/PROD-014-native-app-clients.md')}">→ Native app clients & integration ladder</a>
      <a class="lcard" href="${gh('/blob/main/engineering-bible/docs/product/PROD-015-voice-agent.md')}">→ Voice agent & typed actions</a>
      <a class="lcard" href="${gh('/blob/main/engineering-bible/docs/architecture/ARCH-022-layer-manifest-and-capabilities.md')}">→ Capability model</a>
      <a class="lcard" href="${gh('/blob/main/engineering-bible/docs/architecture/AOS-ARCH-005.md')}">→ IDL & type system</a>
    </div>
    <a class="lane-back" href="#home">← All audiences</a>
  </section>`;
}

function investorsLane(){
  nav('investors');
  app.innerHTML = `
  <section class="lane-page">
    <div class="lane-head lane-head-invest">
      <div class="lane-eyebrow">03 · Investors</div>
      <h1>A phone that owns its stack — and de-risks the hard part.</h1>
      <p class="lane-lede">The wedge is an operating system organized around your work, not apps. The strategy separates a fast, low-risk product track (in emulation today) from slow hardware bring-up — so value ships without being hostage to silicon.</p>
    </div>
    <div class="lane-two">
      <div class="ltile"><h3>The wedge</h3><p>Entity-and-agent OS with inspectable agents and local-first authority — a category difference from iOS/Android app silos, not a feature difference.</p></div>
      <div class="ltile"><h3>Two-track de-risking</h3><p>Product runs in emulation now; a pre-certified module "demo brick" carries the OS on real radios years before a custom device. Almost no reverse-engineering on the critical path.</p></div>
      <div class="ltile"><h3>Business model</h3><p>Subscription sells storage <i>and</i> elastic server compute; a mid-range device plus subscription can feel like a flagship — widening the hardware design space. Self-host tier proves it's a protocol, not a trap.</p></div>
      <div class="ltile"><h3>Honest ceilings</h3><p>Camera is "decent," not flagship, without closed tuning; the demo brick is a demonstration device, not a security product. Claims are evidence-gated, not marketing.</p></div>
    </div>
    <div class="lane-cards">
      <a class="lcard" href="${gh('/blob/main/engineering-bible/docs/product/PROD-013-compute-subscription-and-offload.md')}">→ Compute subscription & offload</a>
      <a class="lcard" href="${gh('/blob/main/engineering-bible/docs/research/RES-011-interim-hardware-market-survey.md')}">→ Market survey & sourcing</a>
      <a class="lcard" href="#compare">→ iOS / Android / Agent OS comparison</a>
      <a class="lcard" href="#gantt">→ Roadmap & phases</a>
    </div>
    <p class="lane-disclaimer">This is a research-and-engineering programme. Nothing here claims a shipping product, certification, or financial projection; it documents intent, strategy, and evidence gates.</p>
    <a class="lane-back" href="#home">← All audiences</a>
  </section>`;
}

function usersLane(){
  nav('users');
  app.innerHTML = `
  <section class="lane-page">
    <div class="lane-head lane-head-user">
      <div class="lane-eyebrow">04 · Early users</div>
      <h1>A calmer phone that works for you.</h1>
      <p class="lane-lede">Not a grid of apps fighting for attention. Your projects, notes, people and plans are the interface; a voice agent you can actually inspect does the busywork; and the device can drop into simple, distraction-free modes in seconds.</p>
    </div>
    <div class="lane-two">
      <div class="ltile"><h3>A voice agent you can trust</h3><p>Ask it to do things across your whole system. Every action is visible, reversible, and logged — and a hardware switch physically cuts the microphone. It can't hear you when muted, by wiring, not policy.</p></div>
      <div class="ltile"><h3>Instant modes</h3><p>Reboot into a typewriter, reader, calculator or remote in seconds. No radios, no feeds, no notifications — focus on purpose, and stretch the battery for days.</p></div>
      <div class="ltile"><h3>Days of standby</h3><p>An always-on low-power island keeps time and watches for wake events while the main computer sleeps fully — hours become days.</p></div>
      <div class="ltile"><h3>Privacy you can verify</h3><p>Local-first: it works offline, your data lives on the device, and anything sent to a server is a visible, consented choice with a receipt — never a silent default.</p></div>
    </div>
    <div class="lane-cards">
      <a class="lcard" href="${gh('/blob/main/engineering-bible/docs/product/PROD-015-voice-agent.md')}">→ How the voice agent works</a>
      <a class="lcard" href="${gh('/blob/main/engineering-bible/docs/architecture/ARCH-021-layered-boot-and-instant-modes.md')}">→ Instant modes</a>
      <a class="lcard" href="${gh('/blob/main/engineering-bible/docs/legal/LEGAL-013-threat-model-and-security.md')}">→ What privacy actually means here</a>
    </div>
    <a class="lane-back" href="#home">← All audiences</a>
  </section>`;
}
