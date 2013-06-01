#include "colors.inc"

global_settings { assumed_gamma 1.0 }
global_settings { ambient_light rgb<.3, .3, .3> }

// ----------------------------------------

camera {
  location  <0.0, 0.0, 2.92 + .05 * clock>
  up y sky y
  right x
  look_at   <0.0, 0.0, 0.0> 
  angle 40
}

light_source {
 <1, 3, 1>
 color rgb <1,1,1>
}   

sphere {
  0, 1
  pigment { color rgb <0.9 0.3 0.1> }
  finish { phong 1.0 phong_size 10 }
}
