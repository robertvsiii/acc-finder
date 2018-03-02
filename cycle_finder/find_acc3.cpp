#include <iostream>
#include <sstream>
#include <string>
#include <iterator>
#include <fstream>
#include <vector>
#include <algorithm> // for std::copy

int main(int argc, char* argv[])
{
    std::string folder(argv[1]);
    std::string filename;
    filename = folder + "A.csv";
    std::ifstream infile(filename);
    std::vector< std::vector<bool> > A;
    std::vector< std::vector<int> > cycles;

    std::string line;
    while (std::getline(infile, line))
    {
        std::istringstream iss(line);
        std::string el;
        std::vector<bool> numbers;
        while (std::getline(iss,el,',')){
            numbers.push_back( el == "1");
        }
        A.push_back(numbers);
    }
    infile.close();
    
    std::ofstream outfile;
    filename = folder + "acc3.csv";
    outfile.open (filename);
    for(int i = 0; i < A.size(); i++){
        for(int j = 0; j < i; j++){
            for(int k = 0; k < i; k++){
                if(k != j){
                    if(A[i][j]*A[j][k]*A[k][i] == 1){
                        outfile << i+1 << ",";
                        outfile << j+1 << ",";
                        outfile << k+1;
                        outfile << "\n";
                    }
                }
            }
        }
    }
    outfile.close();
    
}
