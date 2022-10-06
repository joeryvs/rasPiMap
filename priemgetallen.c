#include <stdlib.h>
#include <stdio.h>

int Ispriem(int num)
{
    for (int i = 2; i < num; i++)
    {
        if (num % i == 0)
        {
            return 0;
        }
    }
    return 1;
}

int main(int argc, char const *argv[])
{
    for (size_t i = 0; i < argc; i++)
    {
        printf("%s\n",argv[i]);
    }

    int count = 2000;
    if (argc == 2)
    {
        count = atoi(argv[1]);
    }
    
    for (int i = 1; i < count; i++)
    {
        if (Ispriem(i))
        {
            printf("%d\n", i);
        }
        else
        {
            printf("\n");
        }
    }

    return 0;
}
