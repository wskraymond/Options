# Barrier Options

#### Reference Formula
![Alt text](./options_formula_1.GIF?raw=true "Call Options PV Discounted from last period")
![Alt text](./options_formula_2.GIF?raw=true "Call Options Price At Day 0")
![Alt text](./options_formula_3.GIF?raw=true "Binomial Tree")

#Complexity Analysis
1. Vanilla: Bottom-UP DP + 2D numpy Array
   * Time complexity: N^2
   * Space complexity: N^2
2. Knock-out: Bottom-UP DP + 1D numpy Array
   * Time complexity: N^2
   * Space complexity: N
3. Knock-out: Vanilla 2D numpy Array + DFS  
   * Time complexity: exponential
   * Space complexity: Vanilla 2D numpy Array

## Limitation
1. Precision Loss
2. N cannot be too large (i.e N=12 is used in test cases)

## Test Case Sample (Knock-out Call + Knock-in Call = Vanilla Call)

```bash
============================= test session starts =============================
collecting ... collected 1 item

test_options.py::MyTestCase::test_knockin_knockout_parity PASSED         [100%]
--------------------Input Parameter-----------------------------------------------------------
risk_free_rate= 0.009950330853168092 vol= 0.26236426446749106 N= 12 spot= 100.0 K= 95.0 T= 1.0 H= 105.0 shares= 100
--------------------Computation---------------------------------------------------------------
Vanilla Call PV at t=0:  518.7218479193812
Up-And-In Call PV at t=0:  423.75315144940305
Up-And-out Call PV at t=0:  94.96869646997808
--------------------Equality for Knock-out + Knock-in = Vanilla --------------------------
knock_out_pv+knock_in_pv =  518.7218479193812 , vanilla_pv =  518.7218479193812
--------------------End ------------------------------------------------------------------


============================== 1 passed in 0.13s ==============================
```

## Dynamic Programming
0. Parameters

    * T = Tenor(Years)
    * n = #no of periods (e.g days)
    * i = period i (n...0) //0 is 0th(start of day), i is ith(end of day), n is nth(end of day)
    * j = node j at period i (0...i)
    * r = continuously compounded interest rate log(1+x)
    * df = e^-h*r  #discount factor for 1 period
    * k = strike
    * b = barrier
    * brt = barrier type (in/out)
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
