library(zoo)
library(randomForest)
library(data.table)

speedDistribution <- function(trip)
{
  vitesse = 3.6*sqrt(diff(trip$x,20,1)^2 + diff(trip$y,20,1)^2)/20
  velocity_x <- diff(trip$x) ; velocity_y <- diff(trip$y)
  
  distance <- sqrt(velocity_x^2 + velocity_y^2)
  vitesse <- rollapply(distance, width = 10, FUN = median) * 3.6 # Smoothing
  
  acceleration_x <- diff(velocity_x) ; acceleration_y <- diff(velocity_y)
  accel <- sqrt(acceleration_x^2 + acceleration_y^2)
  acceleration <- rollapply(accel, width = 10, FUN = median) * 3.6 # Smoothing
  
  position_x <- trip$x ; position_y <- trip$y
  departure <- c(trip$x[1], trip$y[1])
  arrival <- c(tail(trip$x, 1), tail(trip$y, 1))
  delta_x <- diff(position_x) ; delta_y <- diff(position_y)
  
  distance2 <- sum(sqrt(delta_x^2 + delta_y^2))
  manhattan_distance <- sum(abs(arrival - departure))
  euclidian_distance <- sum(sqrt((arrival - departure)^2))
  at <- TangAccelDistribution(trip,1)
  cd <- curvatureDistribution(trip,0)
  
  f1 <- quantile(vitesse, seq(0.05, 1, by = 0.05))
  f2 <- quantile(acceleration, seq(0.05, 1, by = 0.05))
  f3 <- manhattan_distance
  f4 <- euclidian_distance
  f5 <- distance2
  feat <- c(f1, f2, f3, f4, f5, at, cd)
  names(feat) <- paste("f", 1:83, sep="")
  return(feat)    
  
}

drivers = list.files("S:/Kaggle/Competition 3/drivers")
randomDrivers = sample(drivers, size = 5)

refData = NULL
target = 0
names(target) = "target"
for(driver in randomDrivers)
{
  dirPath = paste0("S:/Kaggle/Competition 3/drivers/", driver, '/')
  for(i in 1:200)
  {
    trip = read.csv(paste0(dirPath, i, ".csv"))
    features = c(speedDistribution(trip), target)
    refData = rbind(refData, features)
  }
}

target = 1
names(target) = "target"
submission = NULL
for(driver in drivers)
{
  print(driver)
  dirPath = paste0("S:/Kaggle/Competition 3/drivers/", driver, '/')
  currentData = NULL
  for(i in 1:200)
  {
    trip = read.csv(paste0(dirPath, i, ".csv"))
    features = c(speedDistribution(trip), target)
    currentData = rbind(currentData, features)
  }
  train = rbind(currentData, refData)
  train = as.data.frame(train)
  train[is.na(train)] <- 0
  g = randomForest(train[,1:83], y = as.factor(train[,84]), ntree = 1000, mtry = 12)
  currentData = as.data.frame(currentData)
  # This is not the good way to have the training error but I used it for the ~0.84 score
  # p = predict(g, currentData, type = "prob")[,2]
  p <- predict(g, type = "prob")[1:200,2] # Good way (OOB error)
  labels = sapply(1:200, function(x) paste0(driver,'_', x))
  result = cbind(labels, p)
  submission = rbind(submission, result)
}

colnames(submission) = c("driver_trip","prob")
write.csv(submission, "S:/Kaggle/Competition 3/submission8p1.csv", row.names=F, quote=F)
