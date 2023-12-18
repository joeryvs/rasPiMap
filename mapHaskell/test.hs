
faculteit :: Int -> Int
faculteit 0 = 1
faculteit n = n * faculteit (n-1)


fibbonacia :: Int -> Int
fibbonacia 0 = 0
fibbonacia 1 = 1
fibbonacia n = fibbonacia (n-1) + fibbonacia ( n-2)

getlijst :: Int -> [Int]
getlijst 0 = [0]
getlijst n = getlijst(n-1) ++ [n]



ackerman :: Int -> Int -> Int
ackerman 0 n = n+1
ackerman m 0 = ackerman (m-1) 1
ackerman m n = ackerman (m-1) (ackerman m (n-1) )


ispriem :: Int -> Bool
ispriem 0 = False
ispriem 1 = False
ispriem 2 = True
ispriem n = True

main = do 
    print( map fibbonacia (getlijst 9))
    print( ackerman 1 3)