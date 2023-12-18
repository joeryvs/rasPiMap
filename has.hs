
indentity :: Int -> Int
indentity a = a

dubbel :: (a->a->a) -> a -> a
dubbel func var = func var var


multiply :: Int -> Int -> Int
multiply x y = x * y

kwadraat :: Int -> Int
kwadraat  = dubbel (*)  

main :: IO()
main = do
    print (kwadraat 5)