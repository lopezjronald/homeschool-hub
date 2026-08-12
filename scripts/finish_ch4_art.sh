#!/usr/bin/env bash
# Finish the Dimensions Math 3A Chapter 4 manga art (HH-167).
#
# 13 panels were never drawn and 28 more need redrawing after the vision-QC pass;
# both stalled when Replicate began returning ModelRateLimitError (E003). That
# message means low credit at least as often as it means real demand — check
# https://replicate.com/account/billing first, then run this from the repo root.
#
#     bash scripts/finish_ch4_art.sh            # local curriculum 6
#     bash scripts/finish_ch4_art.sh 1          # a different curriculum id
#
# Safe to re-run: a plain generate only draws panels that have no art, and each
# --only list redraws exactly the panels the QC pass rejected.
set -uo pipefail

CUR="${1:-6}"
PY=./.venv/Scripts/python.exe
[ -x "$PY" ] || PY=python

run() {  # run <label> <command…>
  local label="$1"; shift
  echo "── $label"
  "$@" 2>&1 | tail -2
}

echo "=== 1. the 13 panels that were never drawn ==="
run "L8 Times as Many"   $PY manage.py generate_pokemon_ch4_l8_times_as_many --curriculum "$CUR" --delay 30
run "L9 Two Steps"       $PY manage.py generate_pokemon_ch4_l9_two_step      --curriculum "$CUR" --delay 30

echo
echo "=== 2. the 28 panels the QC pass rejected (wrong counts / arrangements) ==="
run "L1 p3,4,5,7"        $PY manage.py generate_pokemon_ch4_l1_equal_groups            --only 3,4,5,7     --curriculum "$CUR" --delay 30
run "L2 p1,2,4,5,6"      $PY manage.py generate_pokemon_ch4_l2_product_strategies      --only 1,2,4,5,6   --curriculum "$CUR" --delay 30
run "L3 p1,4,6,8"        $PY manage.py generate_pokemon_ch4_l3_division_meanings       --only 1,4,6,8     --curriculum "$CUR" --delay 30
run "L4 p1,3,4,5,6,7"    $PY manage.py generate_pokemon_ch4_l4_zero_and_one            --only 1,3,4,5,6,7 --curriculum "$CUR" --delay 30
run "L5 p1,2,4,5,6,7"    $PY manage.py generate_pokemon_ch4_l5_remainders              --only 1,2,4,5,6,7 --curriculum "$CUR" --delay 30
run "L6 p2,6,7"          $PY manage.py generate_pokemon_ch4_l6_odd_even                --only 2,6,7       --curriculum "$CUR" --delay 30

echo
DRAWN=$(ls static/manga/pokemon-ch4-*/p*.jpg 2>/dev/null | wc -l)
echo "=== drawn: ${DRAWN}/72 ==="
if [ "$DRAWN" -eq 72 ]; then
  cat <<'NEXT'

All 72 present. To ship:
  1. Re-run the visual QC before trusting the new panels (the model misses ~50%
     of diagram panels; L7-L9 have never been QC'd at all).
  2. git add static/manga/pokemon-ch4-*/ && git commit
  3. git push heroku <branch>:main
  4. heroku run --app steadfast-scholars \
       "python manage.py generate_pokemon_ch4_l8_times_as_many --link-only --curriculum 1 && \
        python manage.py generate_pokemon_ch4_l9_two_step      --link-only --curriculum 1"
     (L1-L7 are already linked; re-linking them is harmless but unnecessary.)

NEXT
else
  echo "Still short. Re-run once credit is topped up — nothing here is destructive."
fi
