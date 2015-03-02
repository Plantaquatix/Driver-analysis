library(shapes)
# Very slow (each driver: minimum of 2 hours)

result_final <- matrix(0, ncol = 200, nrow = 200)
for (i in 1:200) {
  ref <- read.csv(paste("S:/Kaggle/Competition 3/drivers/1622/", i, ".csv", sep =""))
  ref <- as.matrix(ref)
  
  for (j in seq((i+1), 200, by = 1)) {
    current <- read.csv(paste("S:/Kaggle/Competition 3/drivers/1622/", j, ".csv", sep =""))
    current <- as.matrix(current)
    minimum <- min(nrow(ref), nrow(current))
    ind_loop <- abs(dim(ref)[1] - dim(current)[1])
    sign_proc <- sign(dim(ref)[1] - dim(current)[1])
    res <- NULL
    if (min(nrow(ref), nrow(current)) / max(nrow(ref), nrow(current)) < 0.6) {sign_proc <- Inf }
    if (sign_proc == 1) {
      
      for (k in seq(1, ind_loop, by = ifelse(round(ind_loop/20) == 0, 1, round(ind_loop/20)))) {
        modelOPA <- procOPA(ref[k:(minimum - 1 + k),], current, scale = FALSE, reflect = TRUE)
        res <- rbind(res, modelOPA$rmsd)
        
      }
    } else if (sign_proc == - 1) {
      
      for (k in seq(1, ind_loop, by = ifelse(round(ind_loop/20) == 0, 1, round(ind_loop/20)))) {
        modelOPA <- procOPA(ref, current[k:(minimum - 1 + k),], scale = FALSE, reflect = TRUE)
        res <- rbind(res, modelOPA$rmsd)
      }
      
    } else if (sign_proc == 0) {
      
      for (k in seq(1, 1, by = 1)) {
        modelOPA <- procOPA(ref, current, scale = FALSE, reflect = TRUE)
        res <- rbind(res, modelOPA$rmsd)
      }
    
    } else {res <- Inf}
    result_final[j, i] <- min(res)
    print(j)
  }
  print(i)
}

