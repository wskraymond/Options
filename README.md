# Barrier Options

#### Binomial Model
![Alt text](images/binomial/options_formula_1.GIF?raw=true "Call Options PV Discounted from last period")
![Alt text](images/binomial/options_formula_2.GIF?raw=true "Call Options Price At Day 0")
![Alt text](images/binomial/options_formula_3.GIF?raw=true "Binomial Tree")

## Complexity Analysis
1. Vanilla: Bottom-UP DP + 2D numpy Array
   * Time complexity: N^2
   * Space complexity: N^2
2. Knock-out: Bottom-UP DP + 1D numpy Array
   * Time complexity: N^2
   * Space complexity: N
3. Knock-in: 
   1. Vanilla 2D numpy Array + DFS with memo
      * Time complexity: N^2 
      * Space complexity: N^2
   2. (TODO) Bottom-up DP to calculate (1) activated node(i,j)'s vanilla price Or (2) if not activated, do as usual 
      * Time complexity: K x N^2
      * Space complexity: N
   
## Limitation
1. N cannot be too large (i.e N=500 is used in test cases)
2. precison (https://docs.python.org/3/library/decimal.html)

## Verification
```bash
# Initialise parameters
S0 = 100  # initial stock price
K = 110  # strike price
T = 0.5  # time to maturity in years
r = np.log(1+0.06)  # annual risk-free rate
sigma = np.log(1+0.3)  # Annualised stock price volatility

periods = range(10, 500, 10) 
```
![Alt text](images/test/convergence_to_bs.GIF?raw=true "Comparison")

## Test Case Sample (Knock-out Call + Knock-in Call = Vanilla Call)
![Alt text](images/binomial/options_formula_4.GIF?raw=true "Parity")

```bash
============================= test session starts =============================
collecting ... collected 1 item

test_options.py::MyTestCase::test_knockin_knockout_parity 

============================== 1 passed in 1.77s ==============================

Process finished with exit code 0
PASSED         [100%]
--------------------Input Parameter-----------------------------------------------------------
risk_free_rate= 0.009950330853168092 vol= 0.26236426446749106 N= 500 spot= 100.0 K= 95.0 T= 1.0 H= 105.0 shares= 1
--------------------Computation---------------------------------------------------------------
Vanilla Call PV at t=0:  13.371077462005541
Up-And-In Call PV at t=0:  13.318153535622839
Up-And-out Call PV at t=0:  0.05292392638270593
--------------------Equality for Knock-out + Knock-in = Vanilla --------------------------
knock_out_pv+knock_in_pv =  13.371077462005545 , vanilla_pv =  13.371077462005541 BS_Model= 13.370147046851775
--------------------End ------------------------------------------------------------------

```

## Dynamic Programming
0. Parameters (used in code)

    * T = Tenor(Years)
    * n = #no of periods (e.g days)
    * i = period i (n...0) //0 is 0th(start of day), i is ith(end of day), n is nth(end of day)
    * j = node j at period i (0...i)
    * r = continuously compounded interest rate log(1+x)
    * df = e^-h*r  #discount factor for 1 period
    * k = strike
    * b = barrier
    * move = movement (up/down)
    * opt = option type  (call/put)
    * sigma = std of continuously compounded stock return (annualized)
    * h = T/n
    * p = risk neutral prob. for up move
    * u = e^sqrt(h)*sigma  #up move
    * d = 1/u              #down move
    * s0 = initial stock price

1. Binomial Tree

    * Overlapped(u * d = 1) nodes  
        * At i = 3(4th day), 4 leaf nodes.
    * total number of up and down movement = n-1
        * At i = 3(4th day), max no. of up = 3 or max no. of down = 3

2. Recursion Relations for PV

   PV(i,j) = df * [ p*PV(i+1, j+1) + (1-p)*PV(i+1,j) ]

3. Stock Price at jth node and ith period

   s(i,j) = s0 * u^j * d^i-j

4. Existence of options at ith period
   > If inout=knock-out 
   >> If (move=up and s(i,j)>=H) or (move=down and s(i,j)<=H)  
   >>> Then PV(i,j) = 0 # terminated
   
   >If inout=knock-in
   >> If (move=up and s(i,j)>=H) or (move=down and s(i,j)<=H)
   >>> Then PV(i,j) = vanilla(i,j) # becomes vanilla options at (i,j)

6. Base case: Payoff at n-1th period (European)
   > If opt=call , 
   >> Then PV(n-1, j) = max{0, s(n-1,j)-K}
   
   > If opt=put , 
   >> Then PV(n-1, j) = max{0, K - s(n-1,j)}

## Options Greek
![Alt text](images/blacksholes/greek.GIF?raw=true "Greek")

## Reference
 * https://blog.slcg.com/2013/01/barrier-options.html
 * https://en.wikipedia.org/wiki/Binomial_options_pricing_model
 * https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model


