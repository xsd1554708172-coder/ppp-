from pathlib import Path
import shutil

src = Path("/mnt/data/ppp_refined_figs_3_v2/Figure_1_enhanced_progress_state_space_refined_v2.png")
dst = Path.cwd() / "Figure_1_enhanced_progress_state_space_refined_v2.png"
shutil.copy2(src, dst)
print(dst)
