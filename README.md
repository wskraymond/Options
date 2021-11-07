# Barrier Options

#### Reference Formula
![Alt text](./options_formula_1.GIF?raw=true "Call Options PV Discounted from last period")
![Alt text](./options_formula_2.GIF?raw=true "Call Options Price At Day 0")
![Alt text](./options_formula_3.GIF?raw=true "Binomial Tree")

## Dynamic Programming - Bottom Down
0. Parameters

    * T = Tenor(Years)
    * n = #no of periods (e.g days)
    * i = period i (n-1...0)
    * j = node j at period i (0...i)
    * r = continuously compounded interest rate 
    * df = e^h*r  #discount factor for 1 period
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
   >If bt=in and s(i,j)<=b, 
   >> Then PV(i,j) = 0 # terminated
   
   > If bt=out and s(i,j)>=b, 
   >> Then PV(i,j) = 0 # terminated
   
   > else exists (non-terminated)

6. Base case: Payoff at n-1th period (European)
   > If opt=call , 
   >> Then PV(n-1, j) = max{0, s(n-1,j)-k}
   
   > If opt=put , 
   >> Then PV(n-1, j) = max{0, k - s(n-1,j)}
