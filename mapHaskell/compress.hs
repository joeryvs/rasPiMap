
compress :: (a->b->b) -> b -> [a]  -> b
compress func identity [] = identity
compress func identity (n:m) = func n (compress func identity m)


som :: [Int] -> Int
    = compress (+) 0 

pproduct :: [Int] -> Int
    = compress (*) 1

faculteit :: Int -> Int
faculteit n = pproduct [1..n]

main :: IO()
main = do 
    print (som [3,4,5])
    print (som [10,20,30])