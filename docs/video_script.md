# Video Presentation Script: ZeroToken Router (Track 1)
**Target Length**: 2 to 3 minutes

---

### **Section 1: Introduction & The Problem**
* **Duration**: 0:00 – 0:35
* **Visual on Screen**: 
  * Show the title slide (Slide 1 from your presentation deck).
  * Then switch your screen to the `Dockerfile` or `src/tokenrouter/agent.py` file.
* **What to Speak**:
  > *"Hi everyone, today we are showcasing **ZeroToken Router**, our submission for Track 1 of the AMD Developer Hackathon: ACT II. 
  > 
  > In enterprise AI pipelines, sending every single user prompt to a premium, cloud-hosted API model is incredibly wasteful and expensive. Simple requests like sentiment analysis, basic entity extraction, or elementary math calculations do not require billions of parameters of compute. 
  > 
  > ZeroToken Router solves this by implementing a fast, zero-token-first routing system that keeps simple tasks local and escalates only when premium reasoning is absolutely necessary."*

---

### **Section 2: Architecture Overview**
* **Duration**: 0:35 – 1:10
* **Visual on Screen**:
  * Display the Mermaid architecture diagram (from Slide 3) or show the package directory structure in VS Code.
* **What to Speak**:
  > *"Our architecture relies on three distinct layers. 
  > 
  > First, a local, deterministic classifier inspects the incoming task prompt on startup. This classification runs instantly and costs zero tokens. 
  > 
  > Second, if the task is classified as sentiment, summarization, entity recognition, or simple math, the router runs it through highly optimized local solvers or a bundled CPU-only Qwen2.5 3B model. 
  > 
  > Third, if a task requires deep reasoning or complex code generation, the agent escalates the query to premium Fireworks AI models—specifically MiniMax M3 and Kimi K2.7 Code. If the remote API fails or times out, the system automatically falls back to local execution to guarantee schema compliance."*

---

### **Section 3: Live Demo & Verification**
* **Duration**: 1:10 – 2:00
* **Visual on Screen**:
  * Open a terminal window in your IDE.
  * Run the command to evaluate the agent:
    `python -m tokenrouter.agent` (with input set to the simulated evaluation tasks).
  * Then immediately run the evaluation script:
    `python scripts/evaluate.py --tasks data/simulated_eval.json --results output/results.json`
  * Show the terminal output printing `PASS` for all 19 tasks.
* **What to Speak**:
  > *"Let's see it in action. I'm running the agent over our 19-task simulated evaluation set. Next, we run the official validator script. 
  > 
  > As you can see on screen, we score a perfect **19 out of 19** on the evaluation set. What's even more impressive is the resource consumption: because over 50% of the tasks were resolved locally via our heuristic solvers, we reduced our external Fireworks API token count by **52.6%**, while the entire batch completed in less than 6 seconds."*

---

### **Section 4: Submission & Compliance**
* **Duration**: 2:00 – 2:30
* **Visual on Screen**:
  * Open the `Dockerfile` and point out the environment variables section and the model downloading logic.
  * Show a preview of the GitHub actions workflow file `publish.yml`.
* **What to Speak**:
  > *"Our solution is fully compliant with the hackathon rules. The Docker container is packaged for the required `linux/amd64` platform. It does not bundle any secret API keys; instead, it dynamically reads the injected variables from the environment during evaluation. 
  > 
  > By keeping execution lightweight, we stay well within the 4 GB RAM and 2 vCPU limits."*

---

### **Section 5: Conclusion**
* **Duration**: 2:30 – 2:45 (End)
* **Visual on Screen**:
  * Show Slide 5 of the presentation deck containing the closing line.
* **What to Speak**:
  > *"In summary, ZeroToken Router turns model selection into automated infrastructure: we prove tasks locally first, and escalate only when necessary. Thank you!"*
