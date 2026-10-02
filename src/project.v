`default_nettype none
// Physical analog macro. This file describes only its external interface.
(* blackbox *)
module silicluster_jonah_2cap_dac(
    input wire VGND, input wire VDPWR,
    input wire charge_high, input wire charge_low, input wire share,
    input wire vref_high, input wire vref_low, output wire vout
);
endmodule
`default_nettype wire
