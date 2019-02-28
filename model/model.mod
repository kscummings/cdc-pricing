# Private game duopoly in surplus scenario

# --- MODEL COMPONENTS ---

set Manufacturers ordered;      # assumes two manufacturers
set Sectors ordered;        	  # public then private

var price{Sectors, Manufacturers} >=0;
var quant{Sectors, Manufacturers} >=0;
var privCap{Manufacturers} >=0;
var governmentCost >= 0;        # so that it can be displayed
var z;                   # bound price difference


param gamma >=0;			# product differentiation
param demand >=0;			# demand

param a{Sectors};			# demand curve constants
param b{Sectors};
param c{Sectors};

param capacity{Manufacturers} >=0;	# total capacity
param profit{Manufacturers} >=0;	  # required profit
param U =					                  # cutoff for BC equilibrium
     a[last(Sectors)]*(1+gamma)/gamma * (1-2*(1-gamma)^(1/2)/((1+gamma)^(1/2)*(2-gamma)));

param objCost >= 0;           # objective function weight for govt cost

# --- OBJECTIVE FUNCTION ---

minimize governmentCostAndPriceDifference:
   (objCost)*governmentCost + (1-objCost)*z;


# --- CONSTRAINTS ---

## Quantities follow linear demand curve
	demandCurve{s in Sectors, m in Manufacturers, j in Manufacturers: m <> j}:
	quant[s,m] = a[s] - b[s]*price[s,m] + c[s]*price[s,j];

## Don't exceed manufacturing capacity in private sector
	privateCapConstraint{m in Manufacturers}:
	quant[last(Sectors),m] <= privCap[m];

## Set private capacity as leftover from public
	privateCapacity{m in Manufacturers}:
	privCap[m] = capacity[m] - quant[first(Sectors),m];

## Bertrand-Chamberlin Equilibrium
	bertrandCapacityConstraint{m in Manufacturers}:
	privCap[m] >= U;

	bertrandPriceConstraint1{m in Manufacturers}:
	price[last(Sectors),m] =
		a[last(Sectors)]/(2*b[last(Sectors)] - c[last(Sectors)]);

	bertrandPriceConstraint2{m in Manufacturers}:
	price[last(Sectors),m] <=
		a[last(Sectors)]/(2*b[last(Sectors)] - c[last(Sectors)]);

## Ensure total public demand is met
  totalPublicDemandConstraint:
  sum{m in Manufacturers}(quant[first(Sectors),m]) >= 0.57*demand;

## Ensure total private demand is met
  totalPrivateDemandConstraint:
	sum{m in Manufacturers}(quant[last(Sectors),m]) >= 0.43*demand;

## Ensure manufacturers make at least min profit P
	profitThresholdConstraint{m in Manufacturers}:
	sum{s in Sectors}quant[s,m]*price[s,m] >= profit[m];

## Compute government cost
  computeGovtCost:
  governmentCost = sum{m in Manufacturers} price[first(Sectors),m]*quant[first(Sectors),m];

## Bound price difference
  firstLarger:
  price[first(Sectors),last(Manufacturers)]-price[first(Sectors),first(Manufacturers)] <= z;

  lastLarger:
  price[first(Sectors),first(Manufacturers)]-price[first(Sectors),last(Manufacturers)] <= z;
