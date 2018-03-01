#include <iostream>
#include <sstream>
#include <string>
#include <iterator>
#include <fstream>
#include <vector>
#include <algorithm> // for std::copy

int main()
{
    std::ifstream infile("A.csv");
    std::vector< std::vector<bool> > A;
    std::vector< std::vector<int> > cycles;
    std::vector<int> reactions (4,0);

    std::string line;
    while (std::getline(infile, line))
    {
        std::istringstream iss(line);
        std::string el;
        std::vector<bool> numbers;
        while (std::getline(iss,el,',')){
            numbers.push_back(el == "1");
        }
        A.push_back(numbers);
    }
    
    for(int i = 0; i < A.size(); i++){
        for(int j = 0; j < i; j++){
            for(int k = 0; k < j; k++){
                for(int l = 0; l < k; l++){
                    if(A[i][j]*A[j][k]*A[k][l]*A[l][i] == 1){
                        reactions[0] = i+1;
                        reactions[1] = j+1;
                        reactions[2] = k+1;
                        reactions[3] = l+1;
                        cycles.push_back(reactions);
                    }
                }
            }
        }
    }
    
    std::ofstream outfile;
    outfile.open ("acc4.csv");
    for(int j = 0; j < cycles.size(); j++){
        for(int m = 0; m < cycles[j].size(); m++){
            outfile << cycles[j][m] << ",";
        }
        outfile << "\n";
    }
    outfile.close();
    
}
