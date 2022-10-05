
pi = 3.14159

print(pi)
print("Hello world")

function isPriem(num)
    for i = 2,(num-1) do
        if (num%i==0) then 
            return false
        end
    end
    return true
end


for a = 1,1000 do
    if isPriem(a) then
        print(a)
    end
end