---
name: verilog-fpga-digital-design
metadata:
  category: Hardware Design and EDA FPGA
description: Design, synthesize, and verify digital hardware circuits using Verilog and SystemVerilog for FPGAs (Xilinx Artix/Zynq, Intel Cyclone, Lattice iCE40). Implement synthesizable finite state machines (FSM), synchronous reset logic, clock domain crossing (CDC) synchronizers, and testbench simulation using Icarus Verilog and GTKWave. Trigger when writing Verilog HDL, designing FPGA logic, or debugging hardware timing.
compatibility: IEEE 1364-2005 (Verilog), IEEE 1800 (SystemVerilog), Icarus Verilog, Yosys
---

# Verilog & FPGA Digital Design Skill Guide

This skill governs standard, synthesizable digital hardware description and simulation workflows for FPGA architectures.

---

## 1. Synchronous Digital Circuit Architecture

All synthesizable logic must be driven by positive clock edges, with zero inferred latches.

```text
[ Clock Input (clk) ] --------------------------------------------+
                                                                  |
[ Asynchronous / Synchronous Reset (rst_n) ]                      |
                                                                  |
[ Inputs ] ---> [ Combinational Next-State Logic ] ---> [ D Flip-Flops (Registers) ] ---> [ Output Logic ]
                       ^                                         |
                       |-------------- State Feedback -----------+
```

---

## 2. Production Synthesizable Verilog Patterns

### A. 3-Always Block Mealy/Moore Finite State Machine (FSM)

```verilog
`default_nettype none

module uart_rx_fsm (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       rx_serial,
    output reg  [7:0] rx_byte,
    output reg        rx_ready
);

    // State Encoding
    localparam [1:0] STATE_IDLE  = 2'b00,
                     STATE_START = 2'b01,
                     STATE_DATA  = 2'b10,
                     STATE_STOP  = 2'b11;

    reg [1:0] current_state, next_state;
    reg [2:0] bit_index;
    reg [7:0] shift_reg;

    // 1. Synchronous State Register (Sequential)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_state <= STATE_IDLE;
            bit_index     <= 3'd0;
            rx_byte       <= 8'd0;
            rx_ready      <= 1'b0;
        end else begin
            current_state <= next_state;

            // Sequential datapath updates
            if (current_state == STATE_DATA) begin
                shift_reg[bit_index] <= rx_serial;
                bit_index <= bit_index + 1'b1;
            end else if (current_state == STATE_STOP) begin
                rx_byte  <= shift_reg;
                rx_ready <= 1'b1;
            end else begin
                rx_ready <= 1'b0;
                bit_index <= 3'd0;
            end
        end
    end

    // 2. Combinational Next-State Logic
    always @(*) begin
        next_state = current_state;
        case (current_state)
            STATE_IDLE: begin
                if (!rx_serial) // Start bit detected (low)
                    next_state = STATE_START;
            end
            STATE_START: begin
                next_state = STATE_DATA;
            end
            STATE_DATA: begin
                if (bit_index == 3'd7)
                    next_state = STATE_STOP;
            end
            STATE_STOP: begin
                if (rx_serial) // Valid stop bit (high)
                    next_state = STATE_IDLE;
            end
            default: next_state = STATE_IDLE;
        endcase
    end

endmodule
```

### B. Dual Flip-Flop Clock Domain Crossing (CDC) Synchronizer

```verilog
module cdc_synchronizer (
    input  wire clk_dest,
    input  wire rst_dest_n,
    input  wire async_signal_in,
    output wire sync_signal_out
);

    (* ASYNC_REG = "TRUE" *) reg stage1_reg;
    (* ASYNC_REG = "TRUE" *) reg stage2_reg;

    always @(posedge clk_dest or negedge rst_dest_n) begin
        if (!rst_dest_n) begin
            stage1_reg <= 1'b0;
            stage2_reg <= 1'b0;
        end else begin
            stage1_reg <= async_signal_in;
            stage2_reg <= stage1_reg;
        end
    end

    assign sync_signal_out = stage2_reg;

endmodule
```

---

## 3. FPGA Digital Design Rules

1. **No Inferred Latches:** In combinational `always @(*)` blocks, assign a default value to every signal at the beginning of the block, and specify all `case` branches (or include `default:`) to prevent latches.
2. **Never Use Asynchronous Logic in Counters:** Never drive flip-flop clock pins using combinatorial signals; always use a global clock with a clock-enable signal (`if (enable) counter <= counter + 1`).
3. **Use CDC Synchronizers:** Every single-bit signal originating from an external pin or a different clock domain must pass through at least a 2-stage synchronizer (`ASYNC_REG = "TRUE"`) before consumption.
