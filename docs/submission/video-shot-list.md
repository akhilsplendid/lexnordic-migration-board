# LexNordic Submission Video Shot List

Final local cut: `video/lexnordic-product-demo.mp4`, a 1:34 silent product walkthrough with on-screen captions.

Earlier montage: `video/lexnordic-silent-demo.mp4`. Use the product walkthrough for submission, not the montage.

## Recording Setup

- Frontend: `http://127.0.0.1:5173/#/chat`
- Backend: `http://127.0.0.1:8000`
- Use a fictional applicant and fictional evidence only.
- Keep the browser zoom at 100 percent.
- Avoid showing `.env.local`, cloud dashboards, API keys, private PDFs, or local Downloads paths.

## Timeline

### 0:00-0:15 - Opening

Show the Higgsfield final poster or first app screen.

On-screen text: `Migration stress starts before the form. Rules change. Documents are scattered. Deadlines are unclear. A user needs one place to understand the next action.`

### 0:15-0:40 - User Consultation

Open `/#/chat`, start or select a user session, and type a migration question such as:

`I have a Swedish work permit question. My salary may be below the new threshold and I need to know what evidence I should prepare.`

Show that the platform behaves like a real consultation surface, not just a static dashboard.
Show live Route/Documents/Sources/Risks/Packet checks moving while the answer streams. Keep the default user view simple, then open `Show how this was checked` briefly so judges see proof without confusing the user flow.

### 0:40-1:00 - Route And Matter Workspace

Open the matter workspace and route page. Show route screening, route confidence, and required evidence.

On-screen text: `The user does not need to know the legal route up front. The platform creates a structured matter workspace and keeps the consultation context attached to that user session.`
Show the route catalog board and June 2026 rule overlay so the route page reads as a product page, not a single reused dashboard section.

### 1:00-1:45 - Band Ops Theater

Open `/#/theater` and click `Run Band theater`.

Show:

- Pixel agents passing the case-file baton.
- Pause, replay, and speed controls for the theater.
- Band hub in the middle.
- Judge Proof panel.
- Remote agent count.
- Handoff count.
- Source references and readiness state.
- Event ladder moving through Intake, Evidence, Sources, Risk, and Packet.

On-screen text: `Band is the actual coordination layer. Each role has a responsibility and the UI makes handoffs visible.`

### 1:45-2:15 - AI Packet

Open the Packet or Review page and show the output from the coordinated run: checklist, missing evidence, source trail, and packet readiness.

On-screen text: `The system prepares an AI consultation packet. It does not file automatically with an authority.`
Show the stack proof panel again to reinforce that the packet is connected to Band coordination, source retrieval, provider routing, and the private vault.

### 2:15-2:40 - Architecture

Show the Higgsfield architecture visual or the 12-second architecture teaser.

On-screen text: `React, FastAPI, Supabase, Qdrant, Band remote agents, AI/ML API, and Featherless AI. Qdrant grounds retrieval. Supabase owns user state. Band coordinates the agents.`

### 2:40-3:00 - Close

Show the Theater or cover again.

On-screen text: `LexNordic can grow into a consultation platform across Swedish migration routes, built for people who need clarity before the process becomes overwhelming.`

## Must-Capture Proof

- The user starts from chat.
- The founder story is clear in the opening.
- The live streaming checks are visible while the answer is being generated.
- The same matter context reaches the workspace.
- Band Ops Theater visibly runs.
- At least three agents are shown collaborating through Band.
- The proof panel shows handoffs and source refs.
- The output is a consultation packet, not a fictional filed application.
