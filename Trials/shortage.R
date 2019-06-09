library(readr)
library(tidyverse)

# private sector functions
priv_price <- function(prod_sim){
  (34.143+10.53*prod_sim)*(1-prod_sim)/(2-prod_sim)
}
priv_quant <- function(prod_sim) {
  (3.414+1.053*prod_sim)/((1+prod_sim)*(2-prod_sim))*10^6
}
alpha_pub <- function(prod_sim) {
  (1.396*(1+prod_sim)+1.526)*10^6
}
U <- function(prod_sim) {
  (3.414+1.053*prod_sim)/prod_sim*
    (1-2*(1-prod_sim)^0.5/((1+prod_sim)^0.5*(2-prod_sim)))*10^6
}

# get data
shortage <- read_csv("toy_shortage_base/toy_shortage_base_results.csv") %>%
  select(prod_sim,
         m1_old_price=m1_pub_price,m2_old_price=m2_pub_price,
         m1_old_quant=m1_pub_quant,m2_old_quant=m2_pub_quant) %>%
  mutate(prod_sim=round(prod_sim,1))
inf_sh <- read_csv("toy_shortage_infanrix_revised/toy_shortage_infanrix_revised_results.csv") %>%
  mutate(prod_sim=round(prod_sim,1))%>%
  left_join(shortage,by='prod_sim') %>%
  filter(m1_cap <= 4034000)

# plot shortage metrics
inf_sh%>%
  mutate(savings=((m1_old_price*(m1_cap-U(prod_sim))+m2_old_price*m2_old_quant)-govt_cost)/govt_cost)%>%
  mutate(naive_feas=(m1_old_price*(m1_cap-U(prod_sim))+m1_priv_price*m1_priv_quant)>=m1_prof)%>%
  ggplot(aes(x=m1_old_quant-m1_cap+U(prod_sim),y=savings))+
  geom_line(aes(linetype=as.factor(prod_sim)))+
  geom_point(aes(color=naive_feas),size=2)+
  xlab("Infanrix deficiency")+
  scale_color_discrete("Infanrix profitable")+
  theme_bw()

  