#This function will read in your data set and execute a function you pass in over every n elements in a dataset
# and will return a new vector with the new values. So for instance if you pass in mean as func it will calculate
# the mean of every n elements in the dataset and then return a new vector of those mean values

functionvector <- function(func, n, dataset){
z <- 0
numreads <- 1
count <- {}
ilat <- {}
inc <- function(x)
{
  eval.parent(substitute(x <- x + 1))
}
while(z < (length(dataset)-1)) {
  if(numreads < (n-1)){
    count <- append(count, dataset[z])
    inc(numreads) 
    inc(z)
  } else{
    ilat <- append(ilat,func(count, na.rm = TRUE))
    numreads <- 0
    count <- {}
    inc(z) 
  }
}
return(ilat)
}