# Generates the CSV files used by main.tex (all data are synthetic / computed, not measured).
# Run from this folder:  powershell -File generate_data.ps1
$ci = [System.Globalization.CultureInfo]::InvariantCulture
function F($x, $fmt = 'E6') { $x.ToString($fmt, $ci) }
$here = $PSScriptRoot

# 1. Convergence of three one-step methods on y' = y, y(0) = 1, error at t = 1
function Step-Euler($n) { $h = 1.0 / $n; $y = 1.0; for ($i = 0; $i -lt $n; $i++) { $y += $h * $y }; $y }
function Step-Heun($n)  { $h = 1.0 / $n; $y = 1.0; for ($i = 0; $i -lt $n; $i++) { $k1 = $y; $k2 = $y + $h * $k1; $y += $h / 2 * ($k1 + $k2) }; $y }
function Step-RK4($n)   { $h = 1.0 / $n; $y = 1.0; for ($i = 0; $i -lt $n; $i++) { $k1 = $y; $k2 = $y + $h / 2 * $k1; $k3 = $y + $h / 2 * $k2; $k4 = $y + $h * $k3; $y += $h / 6 * ($k1 + 2 * $k2 + 2 * $k3 + $k4) }; $y }
$lines = @('h,euler,heun,rk4')
foreach ($n in 4, 8, 16, 32, 64, 128, 256) {
  $lines += ('{0},{1},{2},{3}' -f (F (1.0 / $n)), (F ([math]::Abs([math]::E - (Step-Euler $n)))), (F ([math]::Abs([math]::E - (Step-Heun $n)))), (F ([math]::Abs([math]::E - (Step-RK4 $n)))))
}
$lines | Set-Content (Join-Path $here 'convergence.csv') -Encoding ascii

# 2. Lotka-Volterra predator-prey model integrated with RK4
$a = 1.0; $b = 0.1; $d = 0.075; $g = 1.5
function Deriv($x, $y) { , @(($a * $x - $b * $x * $y), ($d * $x * $y - $g * $y)) }
$x = 10.0; $y = 5.0; $dt = 0.01
$lines = @('t,prey,predator')
for ($i = 0; $i -le 3000; $i++) {
  if ($i % 10 -eq 0) { $lines += ('{0},{1},{2}' -f (F ($i * $dt) 'F2'), (F $x 'F4'), (F $y 'F4')) }
  $k1 = Deriv $x $y
  $k2 = Deriv ($x + $dt / 2 * $k1[0]) ($y + $dt / 2 * $k1[1])
  $k3 = Deriv ($x + $dt / 2 * $k2[0]) ($y + $dt / 2 * $k2[1])
  $k4 = Deriv ($x + $dt * $k3[0]) ($y + $dt * $k3[1])
  $x += $dt / 6 * ($k1[0] + 2 * $k2[0] + 2 * $k3[0] + $k4[0])
  $y += $dt / 6 * ($k1[1] + 2 * $k2[1] + 2 * $k3[1] + $k4[1])
}
$lines | Set-Content (Join-Path $here 'predator_prey.csv') -Encoding ascii

# 3. Cost (function evaluations) to reach an error below 1e-6 on y' = y at t = 1
function Min-Steps($growth) {
  $lo = 1; $hi = 4000000
  while ($lo -lt $hi) { $mid = [int][math]::Floor(($lo + $hi) / 2); if ([math]::Abs([math]::E - [math]::Pow((& $growth $mid), $mid)) -le 1e-6) { $hi = $mid } else { $lo = $mid + 1 } }
  $lo
}
$ne = Min-Steps { param($n) 1 + 1.0 / $n }
$nh = Min-Steps { param($n) $h = 1.0 / $n; 1 + $h + $h * $h / 2 }
$nr = Min-Steps { param($n) $h = 1.0 / $n; 1 + $h + $h * $h / 2 + $h * $h * $h / 6 + $h * $h * $h * $h / 24 }
@('method,steps,evals', "Euler,$ne,$($ne * 1)", "Heun,$nh,$($nh * 2)", "RK4,$nr,$($nr * 4)") | Set-Content (Join-Path $here 'cost.csv') -Encoding ascii

# 4. Histogram of 2000 standard normal samples (Box-Muller, fixed seed)
$rng = New-Object System.Random 2026
$n = 2000; $w = 0.5; $counts = @{}
for ($i = 0; $i -lt $n; $i += 2) {
  $u1 = 1.0 - $rng.NextDouble(); $u2 = $rng.NextDouble()
  $r = [math]::Sqrt(-2 * [math]::Log($u1))
  foreach ($z in ($r * [math]::Cos(2 * [math]::PI * $u2)), ($r * [math]::Sin(2 * [math]::PI * $u2))) {
    $bin = [math]::Floor($z / $w)
    if ($bin -ge -8 -and $bin -lt 8) { $counts[[int]$bin] = 1 + [int]$counts[[int]$bin] }
  }
}
# x = left edge of each bin; the last row only closes the final interval (ybar interval)
$lines = @('x,density')
foreach ($bin in -8..7) { $lines += ('{0},{1}' -f (F ($bin * $w) 'F2'), (F (([int]$counts[[int]$bin]) / ($n * $w)) 'F4')) }
$lines += ('{0},{1}' -f (F (8 * $w) 'F2'), (F 0.0 'F4'))
$lines | Set-Content (Join-Path $here 'histogram.csv') -Encoding ascii
