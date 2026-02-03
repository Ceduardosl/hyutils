library("openxlsx")
library("pso")

calculo_intensidade <- function(a, b, c, d, TRs, duracoes){
  tabela_intensidades <- data.frame()
  for(i in 1:length(TRs)){
    TR <- TRs[i]
    for(x in 1:length(duracoes)){
      duracao <- duracoes[x]
      intensidade_mm_h <- (a * TR^b)/((duracao + c)^d) 
      tabela_intensidades[x ,i] <- intensidade_mm_h
    } 
  }
  return(tabela_intensidades)
}

erro_quad <- function(par, tabela_observada, TRs, duracoes){
  a <- par[1]
  b <- par[2]
  c <- par[3]
  d <- par[4]
  intensidade_modelada <- calculo_intensidade(a, b, c , d, TRs, duracoes)
  erro2<- sum((intensidade_modelada - tabela_observada)^2)
  return(erro2)
}

#Funcao para calcular a performance do modelo
performance <- function(dados_observados, dados_modelados){
  
  #Erro quadratico
  e2 <- sum((dados_observados-dados_modelados)^2)
  #Correlacao
  corr <- cor(dados_observados,dados_modelados)
  #NASH-SUTCLIFF
  e2_media <- sum((dados_observados-mean(dados_observados))^2)
  NASH <-1 - (e2/e2_media)
  #Adicionar outros se quiser
  perf <- data.frame(E2 = e2, NASH = NASH,Correlacao = corr)
  return(round(perf,3))
}

list_files <- dir("prj_rain/", pattern = ".csv")
output <- c()
for (path in list_files){
  
  name <- sapply(strsplit(path, ".csv"), getElement, 1)
  print(name)
  coefs <- data.frame()
  perform <- data.frame()
  resul <- list()
  
  tabela_precipitacao <- read.table(paste0("prj_rain/",path), sep = ",", header = T)
  duracoes_min <- tabela_precipitacao$duracao
  duracoes_hr <- duracoes_min/60
  
  tabela_precipitacao <- tabela_precipitacao[,c(-1)]
  TRs <- as.numeric(gsub("X", "", colnames(tabela_precipitacao)))
  colnames(tabela_precipitacao) <- TRs
  tabela_intensidade <- tabela_precipitacao/duracoes_hr
  
  resul[[name]] <- psoptim(par = vector(mode = "numeric",length = 4),lower = c(0, 0, 0, 0),upper = c(2000, 1, 20, 1),
                        fn = erro_quad,tabela_observada = tabela_intensidade,TRs = TRs,duracoes = duracoes_min,
                        control = list(maxit = 100))
  
  a <- resul[[name]]$par[1]
  b <- resul[[name]]$par[2]
  c <- resul[[name]]$par[3]
  d <- resul[[name]]$par[4]
  
  aux <- cbind(name, a, b, c, d)
  output <- rbind(output, aux)  
}
output <- as.data.frame(output)
write.csv(output, "Coef_IDF.csv", sep = ";")

