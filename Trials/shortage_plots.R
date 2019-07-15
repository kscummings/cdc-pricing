library(tidyverse)
library(readr)

setwd("~/Desktop/Publications/CDC/cdc-pricing/Trials/")
inf_shortage <- read_csv("./Infanrix_shortage/Infanrix_shortage_results.csv")
dap_shortage <- read_csv("./Daptacel_shortage/Daptacel_shortage_results.csv")
sym_shortage <- read_csv("./Symmetric_shortage/Symmetric_shortage_results.csv")

#### COMPUTE NAIVE SCENARIO OUTCOMES

# get pre-shortage info 
pre_inf <- inf_shortage %>% 
  filter(m1_cap==max(m1_cap)) %>% 
  select(m1_pub_price,m2_pub_price,m1_priv_price,m2_priv_price,
         m1_pub_quant,m2_pub_quant,m1_priv_quant,m2_priv_quant,
         dem) %>%
  mutate(surplus=m1_pub_quant+m2_pub_quant+m1_priv_quant+m2_priv_quant-dem)

pre_dap <- dap_shortage %>%
  filter(m2_cap==max(m2_cap)) %>% 
  select(m1_pub_price,m2_pub_price,m1_priv_price,m2_priv_price,
         m1_pub_quant,m2_pub_quant,m1_priv_quant,m2_priv_quant,
         dem) %>%
  mutate(surplus=dem-m1_pub_quant-m2_pub_quant-m1_priv_quant-m2_priv_quant)

pre_sym <- sym_shortage %>%
  filter(m1_cap==max(m1_cap)) %>% 
  select(m1_pub_price,m2_pub_price,m1_priv_price,m2_priv_price,
         m1_pub_quant,m2_pub_quant,m1_priv_quant,m2_priv_quant,
         dem) %>%
  mutate(surplus=dem-m1_pub_quant-m2_pub_quant-m1_priv_quant-m2_priv_quant)


# compute:
#   (1) deficiency
#   (2) govt cost under naive strategy
#   (3) profit earned by low-capacity manufacturer under naive strategy
inf_shortage <- inf_shortage %>%
  mutate(deficiency=case_when(
    m1_cap > pre_inf$m1_pub_quant + pre_inf$m1_priv_quant ~ 0,
    TRUE ~ pre_inf$m1_pub_quant + pre_inf$m1_priv_quant - m1_cap  
  )) %>%
  mutate(naive_govt_cost=case_when( # base govt cost
    deficiency==0 ~ 0,
    TRUE ~ pre_inf$m1_pub_price*(m1_cap-m1_priv_quant)+pre_inf$m2_pub_price*pre_inf$m2_pub_quant
  )) %>%
  mutate(naive_m1_profit=case_when(
    deficiency==0 ~ 0,
    TRUE ~ pre_inf$m1_pub_price*(m1_cap-m1_priv_quant)+m1_priv_price*m1_priv_quant
  )) %>%
  #mutate(naive_govt_cost=case_when(
  #  m1_cap + m2_priv_quant + m2_pub_quant < dem ~ naive_govt_cost+
  #    pre_inf$m2_pub_price*(dem - m1_cap - pre_inf$m2_priv_quant - pre_inf$m2_pub_quant),
  #  TRUE ~ naive_govt_cost
  #))
  #mutate(naive_govt_cost=case_when(
  #  deficiency > m1_cap+m2_cap ~ 0, # m2 cannot produce deficient vaccines
  #  (deficiency == 0) ~ 0,  # naive case doesn't apply
  #  deficiency <= surplus ~ (pre_inf$m1_pub_quant-deficiency)*pre_inf$m1_pub_price + pre_inf$m2_pub_quant*pre_inf$m2_pub_price # still meeting demand
  #  TRUE ~ (pre_inf$m1_pub_quant-deficiency)*pre_inf$m1_pub_price+(pre_inf$m2_pub_quant+deficiency+pre_inf$surplus)*pre_inf$m2_pub_price
  #)) %>%
  #mutate(naive_m1_profit=case_when(
  #  deficiency > m2_cap - pre_inf$m2_pub_quant - pre_inf$m2_priv_quant ~ 0, # m2 cannot produce deficient vaccines
  #  deficiency == 0 ~ 0,  # naive case doesn't apply
  #  TRUE ~ (pre_inf$m1_pub_quant-deficiency)*pre_inf$m1_pub_price + pre_inf$m1_priv_quant*pre_inf$m1_priv_price
  #)) %>%
  mutate(earned_m1_profit=case_when(
    is.na(m1_pub_price) ~ 0,
    TRUE ~ m1_pub_quant*m1_pub_price + m1_priv_quant*m1_priv_price
  ))

dap_shortage <- dap_shortage %>%
  mutate(deficiency=case_when(
    m2_cap > pre_dap$m2_pub_quant + pre_dap$m2_priv_quant ~ 0,
    TRUE ~ pre_dap$m2_pub_quant + pre_dap$m2_priv_quant - m2_cap
  )) %>%
  mutate(naive_govt_cost=case_when( # base govt cost
    deficiency==0 ~ 0,
    TRUE ~ pre_dap$m2_pub_price*(m2_cap-m2_priv_quant)+pre_dap$m1_pub_price*pre_dap$m1_pub_quant
  )) %>%
  mutate(naive_m2_profit=case_when(
    deficiency==0 ~ 0,
    TRUE ~ pre_dap$m2_pub_price*(m2_cap-m2_priv_quant)+m2_priv_price*m2_priv_quant
  )) %>%
  #mutate(naive_govt_cost=case_when(
  #  deficiency +  pre_dap$m1_pub_quant + pre_dap$m1_priv_quant > m1_cap ~ 0, # m1 cannot produce deficient vaccines
  #  deficiency==0 ~ 0, # naive case doesn't apply
  #  TRUE ~ (pre_dap$m2_pub_quant-deficiency)*pre_dap$m2_pub_price+(pre_dap$m1_pub_quant+deficiency)*pre_dap$m1_pub_price
  #)) %>%
  #mutate(naive_m2_profit=case_when(
  #  deficiency > m1_cap - pre_dap$m1_pub_quant - pre_dap$m1_priv_quant ~ 0, # m1 cannot produce deficient vaccines
  #  deficiency==0 ~ 0, # naive case doesn't apply
  #  TRUE ~ (pre_dap$m2_pub_quant-deficiency)*pre_dap$m2_pub_price + pre_dap$m2_priv_quant*pre_dap$m2_priv_price
  #)) %>%
  mutate(earned_m2_profit=case_when(
    is.na(m2_pub_price) ~ 0,
    TRUE ~ m2_pub_quant*m2_pub_price + m2_priv_quant*m2_priv_price
  ))

sym_shortage <- sym_shortage %>%
  mutate(deficiency=case_when(
    m1_cap > pre_sym$m1_pub_quant + pre_sym$m1_priv_quant ~ 0,
    TRUE ~ pre_sym$m1_pub_quant + pre_sym$m1_priv_quant - m1_cap  
  )) %>%
  mutate(naive_govt_cost=case_when( # base govt cost
    deficiency==0 ~ 0,
    TRUE ~ pre_sym$m1_pub_price*(m1_cap-m1_priv_quant)+pre_sym$m2_pub_price*pre_sym$m2_pub_quant
  )) %>%
  mutate(naive_m1_profit=case_when(
    deficiency==0 ~ 0,
    TRUE ~ pre_sym$m1_pub_price*(m1_cap-m1_priv_quant)+m1_priv_price*m1_priv_quant
  )) %>%
  #mutate(naive_govt_cost=case_when(
  #  deficiency > m2_cap - pre_sym$m2_pub_quant - pre_sym$m2_priv_quant ~ 0, # m2 cannot produce deficient vaccines
  #  deficiency == 0 ~ 0,  # naive case doesn't apply
  #  TRUE ~ (pre_sym$m1_pub_quant-deficiency)*pre_sym$m1_pub_price+(pre_sym$m2_pub_quant+deficiency)*pre_sym$m2_pub_price
  #)) %>%
  #mutate(naive_m1_profit=case_when(
  #  deficiency > m2_cap - pre_sym$m2_pub_quant - pre_sym$m2_priv_quant ~ 0, # m2 cannot produce deficient vaccines
  #  deficiency == 0 ~ 0,  # naive case doesn't apply
  #  TRUE ~ (pre_sym$m1_pub_quant-deficiency)*pre_sym$m1_pub_price+m1_priv_quant*m1_priv_price
  #)) %>%
  mutate(earned_m1_profit=case_when(
    is.na(m1_pub_price) ~ 0,
    TRUE ~ m1_pub_quant*m1_pub_price + m1_priv_quant*m1_priv_price
  ))  


####### PLOTS

# plot govt cost as fcn of deficiency
inf_shortage %>%
  gather(scenario,cost,govt_cost,naive_govt_cost)%>%
  filter(!(scenario=="naive_govt_cost" & cost==0)) %>%
  ggplot(aes(x=deficiency,y=cost,linetype=scenario)) +
  geom_line() +
  theme_bw() +
  ylim(c(0,35e6)) +
  xlim(c(0,1.5e6)) +
  labs(x="Infanrix deficiency (vaccine units)",y="Cost (USD)") +
  ggtitle("CDC spending during Infanrix shortage",
          subtitle="Deficiency = capacity falls below quantity promised in contract")+
  scale_linetype_manual("Mitigation strategy",
                        values=c("govt_cost"=1,"naive_govt_cost"=2),
                        labels=c("Optimization model","Naïve"))

dap_shortage %>%
  gather(scenario,cost,govt_cost,naive_govt_cost)%>%
  filter(!(scenario=="naive_govt_cost" & cost==0)) %>%
  ggplot(aes(x=deficiency,y=cost,linetype=scenario)) +
  geom_line() +
  theme_bw() +
  ylim(c(0,35e6)) +
  xlim(c(0,1.5e6))+
  labs(x="Daptacel deficiency (vaccine units)",y="Cost (USD)") +
  ggtitle("CDC spending during Daptacel shortage",
          subtitle="Deficiency = capacity falls below quantity promised in contract")+
  scale_linetype_manual("Mitigation strategy",
                        values=c("govt_cost"=1,"naive_govt_cost"=2),
                        labels=c("Optimization model","Naïve"))

sym_shortage %>%
  gather(scenario,cost,govt_cost,naive_govt_cost)%>%
  filter(!(scenario=="naive_govt_cost" & cost==0)) %>%
  ggplot(aes(x=deficiency,y=cost,linetype=scenario)) +
  geom_line() +
  theme_bw()  +
  ylim(c(0,35e6)) +
  xlim(c(0,1.5e6))+
  labs(x="Manufacturer deficiency (vaccine units)",y="Cost (USD)") +
  ggtitle("CDC spending during shortage in symmetric market",
          subtitle="Deficiency = capacity falls below quantity promised in contract")+
  scale_linetype_manual("Mitigation strategy",
                        values=c("govt_cost"=1,"naive_govt_cost"=2),
                        labels=c("Optimization model","Naïve"))

# look at target profit differences
inf_shortage%>%
  gather(scenario,m1_profit,earned_m1_profit,naive_m1_profit) %>%
  filter(!(m1_profit==0)) %>%
  ggplot(aes(x=deficiency,y=m1_profit,linetype=scenario))+
  geom_line()+
  theme_bw() +
  geom_hline(color="red",yintercept=38.5e6,linetype=3)+
  ylim(c(0,45e6)) +
  xlim(c(0,1.5e6))+
  labs(x="Infanrix deficiency (vaccine units)",y="Infanrix profit (USD)") +
  ggtitle("Infanrix earnings during Infanrix shortage",
          subtitle="Target profit = dotted red line ($38.5M)")+
  scale_linetype_manual("Mitigation strategy",
                        values=c("earned_m1_profit"=1,"naive_m1_profit"=2),
                        labels=c("Optimization model","Naïve")) 

dap_shortage %>%
  gather(scenario,m2_profit,earned_m2_profit,naive_m2_profit)%>%
  filter(!(m2_profit==0)) %>%
  ggplot(aes(x=deficiency,y=m2_profit,linetype=scenario))+
  geom_hline(yintercept=43.5e6,color="red",linetype=3)+
  geom_line()+
  theme_bw()+
  ylim(c(0,45e6)) +
  xlim(c(0,1.5e6))+
  labs(x="Daptacel deficiency (vaccine units)",y="Daptacel profit (USD)") +
  ggtitle("Daptacel earnings during Daptacel shortage",
          subtitle="Target profit = dotted red line ($43.5M)")+
  scale_linetype_manual("Mitigation strategy",
                        values=c("earned_m2_profit"=1,"naive_m2_profit"=2),
                        labels=c("Optimization model","Naïve")) 

sym_shortage %>%
  gather(scenario,m1_profit,earned_m1_profit,naive_m1_profit)%>%
  filter(!(m1_profit==0)) %>%
  ggplot(aes(x=deficiency,y=m1_profit,linetype=scenario))+
  geom_line()+
  theme_bw()+
  geom_hline(yintercept=41e6,color="red",linetype=3)+
  ylim(c(0,45e6)) +
  xlim(c(0,1.5e6))+
  labs(x="Manuf. deficiency (vaccine units)",y="Manuf. profit (USD)") +
  ggtitle("Low-capacity manufacturer earnings during shortage in symmetric market",
          subtitle="Target profit = dotted red line ($41M)")+
  scale_linetype_manual("Mitigation strategy",
                        values=c("earned_m1_profit"=1,"naive_m1_profit"=2),
                        labels=c("Optimization model","Naïve")) 

# plot price changes with optimization strategy
inf_shortage %>%
  gather(manufacturer,pub_price,m1_pub_price,m2_pub_price)%>%
  ggplot(aes(x=deficiency,y=pub_price,linetype=manufacturer))+
  geom_line()+
  theme_bw()+
  ylim(c(0,20))

dap_shortage %>%
  gather(manufacturer,pub_price,m1_pub_price,m2_pub_price)%>%
  ggplot(aes(x=deficiency,y=pub_price,linetype=manufacturer))+
  geom_line()+
  theme_bw()+
  ylim(c(0,20))

sym_shortage %>%
  gather(manufacturer,pub_price,m1_pub_price,m2_pub_price)%>%
  ggplot(aes(x=deficiency,y=pub_price,linetype=manufacturer))+
  geom_line()+
  theme_bw()+
  ylim(c(0,20))

### format plots for paper 
temp <- inf_shortage %>% mutate(scenario="Infanrix") %>% 
  rename(naive_profit=naive_m1_profit,earned_profit=earned_m1_profit)
temp2 <- dap_shortage %>% mutate(scenario="Daptacel") %>%
  rename(naive_profit=naive_m2_profit,earned_profit=earned_m2_profit)
all_shortage <- sym_shortage %>%
  mutate(scenario="Symmetric")%>%
  rename(naive_profit=naive_m1_profit,earned_profit=earned_m1_profit)%>%
  rbind(temp)%>%
  rbind(temp2)

all_shortage%>%
  gather(strategy,cost,govt_cost,naive_govt_cost)%>%
  filter(!(strategy=="naive_govt_cost" & cost==0)) %>%
  ggplot(aes(x=deficiency,y=cost,linetype=strategy)) +
  geom_line(size=1.5) +
  theme_bw()  +
  ylim(c(20e6,35e6)) +
  facet_grid(~scenario) +
  scale_linetype_manual("Strategy",
                        values=c("govt_cost"=1,"naive_govt_cost"=2),
                        labels=c("Optimization model","Naïve")) +
  scale_x_continuous("Deficiency (million units)",
                     limits=c(0,1.5e6),
                     breaks=c(0,5e5,1e6,1.5e6),
                     labels=c("0","0.5","1.0","1.5")) +
  scale_y_continuous("CDC Cost (million USD)",
                     limits=c(20e6,35e6),
                     breaks=c(20e6,25e6,30e6,35e6),
                     labels=c("20","25","30","35")) +
  theme(text=element_text(size=20))

all_shortage %>%
  gather(strategy,deficient_manuf_profit,earned_profit,naive_profit)%>%
  filter(!(deficient_manuf_profit==0)) %>%
  ggplot(aes(x=deficiency,y=deficient_manuf_profit,linetype=strategy))+
  geom_line(size=1.5)+
  theme_bw() +
  facet_grid(~scenario) +
  scale_y_continuous("Profit of manufacturer with shortage (million USD)",
                     limit=c(30e6,45e6),
                     breaks=c(30e6,35e6,40e6,45e6),
                     labels=c("30","35","40","45")) +
  scale_x_continuous("Deficiency (million units)",
                     limits=c(0,1.5e6),
                     breaks=c(0,5e5,1e6,1.5e6),
                     labels=c("0","0.5","1.0","1.5"))  +
  scale_linetype_manual("Strategy",
                        values=c("earned_profit"=1,"naive_profit"=2),
                        labels=c("Optimization model","Naïve")) +
  theme(text=element_text(size=20))
