# B Style Examples

This file shows the intended feel of the balanced handwritten style.

## What "B style" should feel like

- The reader can follow the code top-down.
- The code tells a design story:
  - what is being tracked
  - what decision is made
  - what state moves next
- Helper signals are allowed, but only when they remove cognitive load.
- A long boolean is acceptable if it has a strong semantic name and is used more than once.
- If a helper is used only once and its meaning is local, inline it or rewrite the surrounding block instead.

## Example 1: Good control-path structure

This version follows the current preferred style:

- next-state stays combinational
- stored control/hold behavior stays clocked
- no large output-only combinational block

```verilog
module simple_req_slot (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        req_valid,
    output reg         req_ready,
    input  wire [31:0] req_addr,
    output reg         mem_rd,
    output reg  [31:0] mem_addr,
    input  wire        mem_done,
    output reg         resp_valid,
    input  wire        resp_ready
);

    // State flow:
    //   IDLE
    //     -> WAIT_MEM
    //     -> HOLD_RESP
    //     -> IDLE
    localparam STATE_IDLE     = 2'd0;
    localparam STATE_WAIT_MEM = 2'd1;
    localparam STATE_HOLD_RESP= 2'd2;

    reg [1:0] state;
    reg [1:0] next_state;

    wire req_fire  = req_valid  && req_ready;
    wire resp_fire = resp_valid && resp_ready;

    // Next-state logic only answers one question:
    // where do we go next?
    always @(*) begin
        next_state = state;

        case (state)
            STATE_IDLE: begin
                if (req_fire)
                    next_state = STATE_WAIT_MEM;
            end

            STATE_WAIT_MEM: begin
                if (mem_done)
                    next_state = STATE_HOLD_RESP;
            end

            STATE_HOLD_RESP: begin
                if (resp_fire)
                    next_state = STATE_IDLE;
            end

            default: begin
                next_state = STATE_IDLE;
            end
        endcase
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= STATE_IDLE;
        else
            state <= next_state;
    end

    reg        req_ready;
    reg        mem_rd;
    reg [31:0] mem_addr;
    reg        resp_valid;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            req_ready  <= 1'b1;
            mem_rd     <= 1'b0;
            mem_addr   <= 32'b0;
            resp_valid <= 1'b0;
        end else begin
            // Default one-cycle behavior.
            mem_rd <= 1'b0;

            case (state)
                STATE_IDLE: begin
                    req_ready  <= 1'b1;
                    resp_valid <= 1'b0;

                    if (req_valid) begin
                        mem_rd    <= 1'b1;
                        mem_addr  <= req_addr;
                        req_ready <= 1'b0;
                    end
                end

                STATE_WAIT_MEM: begin
                    req_ready <= 1'b0;

                    if (mem_done)
                        resp_valid <= 1'b1;
                end

                STATE_HOLD_RESP: begin
                    req_ready <= 1'b0;

                    if (resp_ready)
                        resp_valid <= 1'b0;
                end

                default: begin
                    req_ready  <= 1'b1;
                    resp_valid <= 1'b0;
                end
            endcase
        end
    end

endmodule
```

Why this reads well:

- state flow is visible at the top
- `req_fire` and `resp_fire` are short and conventional
- hold behavior is explicit in registers
- the reader can see what persists across cycles
- it avoids reconstructing stateful behavior through a large combinational output block

## When combinational output logic is still fine

Combinational output logic is still fine when it is truly simple, such as:

- pure decode outputs
- immediate select/mux results
- next-state decisions
- local one-pass qualification logic

If used for a larger control/output block, mark it as a deliberate exception.

## Example 1.5: Keep direct decode logic direct

For decode-like logic, avoid inventing helper wires when the final assignment is already the clearest form.

Better:

```verilog
`OP_JAL: begin
    illegal_inst_o = 1'b0;
    link_addr_o    = pc + jal_imm;
    pred_taken_o   = pred_taken_i;
    branch_type_o  = 2'b10;
end
```

Usually worse in this style:

```verilog
wire jal_redirect_target;
wire should_keep_prediction;

assign jal_redirect_target   = pc + jal_imm;
assign should_keep_prediction= pred_taken_i;

`OP_JAL: begin
    illegal_inst_o = 1'b0;
    link_addr_o    = jal_redirect_target;
    pred_taken_o   = should_keep_prediction;
    branch_type_o  = 2'b10;
end
```

Why the second version is worse:

- no real reuse
- no new concept was created
- the reader now has to jump upward to recover a simple local meaning

## Example 2: Should we write long helper wires?

Yes, but only occasionally, and only when the name buys back readability.

This can be acceptable:

```verilog
wire pending_req_matches_input;

assign pending_req_matches_input =
       pending_req_valid
    && (req_write == pending_req_write)
    && (req_addr  == pending_req_addr)
    && (req_wdata == pending_req_wdata)
    && (req_wstrb == pending_req_wstrb);
```

This is acceptable only because:

- the name tells the reader what is being compared
- the formatting makes the compare pattern obvious
- it is easier to read than repeating the same expression in several places

This is less good:

```verilog
wire same_as_pending_req = pending_req_valid
                        && (req_write == pending_req_write)
                        && (req_addr  == pending_req_addr)
                        && (req_wdata == pending_req_wdata)
                        && (req_wstrb == pending_req_wstrb);
```

Why it is weaker:

- the name is a little vague
- the reader still has to decode "same in what sense?"

This is better for B style:

```verilog
// Used to suppress re-latching the exact same request while the old one is still pending.
wire pending_req_matches_input;

assign pending_req_matches_input =
       pending_req_valid
    && (req_write == pending_req_write)
    && (req_addr  == pending_req_addr)
    && (req_wdata == pending_req_wdata)
    && (req_wstrb == pending_req_wstrb);
```

## Rule of thumb for helper wires

Use a helper wire when all of the following are roughly true:

1. the expression has real protocol meaning
2. the name is immediately understandable
3. it is reused or clearly improves a branch

Avoid a helper wire when:

1. it is used only once
2. its name is weaker than the expression itself
3. it creates too many equally important-looking signals at the top of the file
4. several nearby helper wires all follow the same long compare pattern

## Practical preference for this skill

The default preference is:

- keep long compare helpers rare
- accept short semantic helpers like `req_fire`
- if a file starts collecting several `foo_matches_bar` style wires, refactor the owning block instead of adding more
- keep one-step decode outputs direct when they are already easy to read locally

## Example 3: Bad B-style drift

This is the kind of thing to avoid:

```verilog
wire cond0 = a && b;
wire cond1 = cond0 && c;
wire cond2 = cond1 || d;
wire cond3 = cond2 && e;
wire cond4 = cond3 && !f;
```

Problems:

- the names carry no design meaning
- the reader must chase the dependency chain
- this looks machine-expanded instead of hand-structured

## Example 4: Better rewrite

```verilog
wire request_accepted;
wire backend_can_respond;
wire need_to_hold_response;

assign request_accepted   = req_valid && req_ready;
assign backend_can_respond= mem_done;
assign need_to_hold_response = backend_can_respond && !resp_ready;
```

This version is longer, but the meaning is recoverable in one pass.
