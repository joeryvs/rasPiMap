
public class Main{

    public static void main(String[] args) {
        for ( int b = 0; b<400;b++) {
            if (isPriem(b)){
                System.out.println(b);
            }
        }
    }

    public static boolean isPriem(int num){
        for (int i = 2;i<num;i++){
            if (num%i==0){
                return false;
            }
        }
        return true;
    }
}