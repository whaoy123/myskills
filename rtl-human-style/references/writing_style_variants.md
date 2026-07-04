# Writing Style Variants

This file explains three practical RTL writing styles so the user can choose intentionally.

## A. Strong style-guide mode

Closest to `lowRISC` / `OpenTitan`.

Traits:

- consistent suffix rules
- strict block roles
- stronger `_i/_o`, `_d/_q`, `*_q` / `*_d`
- systematic formatting
- good for teams and linting

Example:

```verilog
reg        busy_q, busy_d;
reg [1:0]  state_q, state_d;

always @(*) begin
    busy_d  = busy_q;
    state_d = state_q;

    case (state_q)
        IDLE: begin
            if (req_valid_i && req_ready_o) begin
                busy_d  = 1'b1;
                state_d = WAIT_RSP;
            end
        end
        WAIT_RSP: begin
            if (resp_valid_i && resp_ready_o) begin
                busy_d  = 1'b0;
                state_d = IDLE;
            end
        end
        default: begin
            busy_d  = 1'b0;
            state_d = IDLE;
        end
    endcase
end

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        busy_q  <= 1'b0;
        state_q <= IDLE;
    end else begin
        busy_q  <= busy_d;
        state_q <= state_d;
    end
end
```

Use when:

- many contributors
- heavy review/lint requirement
- long-term platform code

## B. Balanced handwritten mode

Still structured, but less template-heavy.

Traits:

- semantic naming first
- helper wires grouped by meaning
- comments explain intent
- `_d/_q` used only where it helps

Example:

```verilog
reg        busy;
reg [1:0]  state;
reg [1:0]  next_state;

wire req_fire  = req_valid && req_ready;
wire resp_fire = resp_valid && resp_ready;

always @(*) begin
    next_state = state;

    case (state)
        STATE_IDLE: begin
            if (req_fire)
                next_state = STATE_WAIT_RSP;
        end

        STATE_WAIT_RSP: begin
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

always @(posedge clk or negedge rst_n) begin
    if (!rst_n)
        busy <= 1'b0;
    else if (req_fire)
        busy <= 1'b1;
    else if (resp_fire)
        busy <= 1'b0;
end
```

Use when:

- you want code to feel hand-written
- the design is still moderately complex
- readability matters more than pattern purity

## C. Traditional handwritten Verilog mode

Closest to what many FPGA engineers naturally write.

Traits:

- less suffix discipline
- more direct names like `state`, `cnt`, `data_buf`
- comments often carry more context
- can read very naturally when kept tidy
- can become messy if not actively constrained

Example:

```verilog
reg [1:0] state;
reg       busy;

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        state <= IDLE;
        busy  <= 1'b0;
    end else begin
        case (state)
            IDLE: begin
                if (req_valid && req_ready) begin
                    busy  <= 1'b1;
                    state <= WAIT_RSP;
                end
            end

            WAIT_RSP: begin
                if (resp_valid && resp_ready) begin
                    busy  <= 1'b0;
                    state <= IDLE;
                end
            end

            default: begin
                state <= IDLE;
                busy  <= 1'b0;
            end
        endcase
    end
end
```

Use when:

- the team already writes this way
- module logic is not too large
- review depends on human familiarity more than formal consistency

## Recommendation

For this user, the best default is usually between `B` and `C`:

- semantic names
- explicit flow comments
- split responsibilities
- comments for tricky logic
- no forced `_d/_q` everywhere

That gives human readability without drifting into loose, fragile style.
