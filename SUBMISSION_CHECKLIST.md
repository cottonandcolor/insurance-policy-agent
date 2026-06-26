# Final Capstone Submission Checklist

**Author:** Preeti Dave · preetidav@gmail.com · June 2026  
**GitHub:** [github.com/cottonandcolor/insurance-policy-agent](https://github.com/cottonandcolor/insurance-policy-agent)

---

## 1. Final Capstone Report

| Requirement | Status | Location |
|-------------|--------|----------|
| Problem and intended user | ✅ Done | `FINAL_REPORT.md` §1 |
| Goal and scope | ✅ Done | `FINAL_REPORT.md` §2 |
| Final architecture and components | ✅ Done | `FINAL_REPORT.md` §3 |
| Design evolution across program | ✅ Done | `FINAL_REPORT.md` §5 |
| Implementation overview | ✅ Done | `FINAL_REPORT.md` §6 |
| Evaluation methods and results | ✅ Done | `FINAL_REPORT.md` §7 |
| Safety, reliability, human oversight | ✅ Done | `FINAL_REPORT.md` §8 |
| Limitations and future improvements | ✅ Done | `FINAL_REPORT.md` §9 |
| GitHub repository link | ✅ Done | `FINAL_REPORT.md` §10 |

**To submit:** Open `FINAL_REPORT.html` in Chrome → Print → Save as PDF → upload to Canvas.

Alternative: Copy from `FINAL_REPORT.md` into the course Word template from Activity 7.1.

---

## 2. Public GitHub Repository

| Requirement | Status | Location |
|-------------|--------|----------|
| README (project, architecture, setup, usage) | ✅ Done | `README.md` |
| Main code | ✅ Done | `main.py`, `src/`, `api/`, `frontend/` |
| Sample inputs/outputs | ✅ Done | `data/synthetic/`, `data/public/`, `demo-uploads/` |
| Clear run instructions | ✅ Done | README Quick start + CLI sections |
| Tests | ✅ 34/34 pass | `tests/`, `python -m pytest tests/ -q` |

**Before submission:** `git push origin main` (local branch may be ahead of remote).

---

## 3. Final Presentation (8–10 min video)

| Requirement | Status | Location |
|-------------|--------|----------|
| Problem and significance | ✅ Script ready | `PRESENTATION_SPEAKER_SCRIPT.txt` Slide 1–2 |
| System goal | ✅ | Slide 3 |
| Architecture and components | ✅ | Slide 4 |
| Key design decisions | ✅ | Slide 5 |
| Design evolution | ✅ | Slide 6 |
| Evaluation and results | ✅ | Slide 8 |
| GitHub contents | ✅ | Slide 7, 10 |
| Strengths, limitations, next steps | ✅ | Slide 8, 10 |
| Slides | ✅ | `presentation.html` |

**To record:**
1. Open `presentation.html` full screen (arrow keys to advance)
2. Terminal ready: `source .venv/bin/activate && python main.py --dry-run`
3. Follow `PRESENTATION_SPEAKER_SCRIPT.txt` (~9:30 target)
4. Upload to YouTube (unlisted), Vimeo, or Loom

---

## 4. Video Submission Document (Canvas)

| Requirement | Status | Location |
|-------------|--------|----------|
| Video link | ⬜ You record | `VIDEO_SUBMISSION.md` |
| Brief presentation summary | ✅ Draft ready | `VIDEO_SUBMISSION.md` |

**To submit:** Add your video URL to `VIDEO_SUBMISSION.md` → export to PDF → upload to Canvas with the final report.

---

## 5. Optional: 90-Second Elevator Pitch

| Requirement | Status |
|-------------|--------|
| Optional recording | ⬜ Not required |

Condense Slides 1–2 + closing from the speaker script if you choose to record one.

---

## Pre-Submission Verification Commands

```bash
cd capstone
source .venv/bin/activate
python -m pytest tests/ -q          # expect: 34 passed
python main.py --dry-run            # expect: recommends plan_b
git push origin main                # sync GitHub with local
```

---

## Canvas Upload Summary

Upload these two items to Canvas:

1. **Final report PDF** — from `FINAL_REPORT.html` or course template
2. **Video submission PDF** — from `VIDEO_SUBMISSION.md` (with your video URL filled in)

Optional third item: elevator pitch video link (not graded).
