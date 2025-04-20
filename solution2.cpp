#include <bits/stdc++.h>
using namespace std;

#define vvi vector<vector<int>>
#define vi vector<int>
#define pi pair<int, int>

class Node
{
public:
    vvi config;
    int key, cost;

    Node(vvi config, int heuristic, int cost)
    {
        this->config = config;
        this->cost = cost;
        this->key = cost + heuristic;
    }

    bool operator==(const Node &other) const
    {
        return this->config == other.config;
    }

    bool operator<(const Node &other) const
    {
        // Logic reversed for min-heap
        return this->key > other.key;
    }

    void printConfig()
    {
        for (auto row : config)
        {
            for (auto col : row)
            {
                cout << col << " ";
            }
            cout << endl;
        }
    }

    pi findBlankTile(vvi config)
    {
        int size = config.size();
        for (int i = 0; i < size; i++)
        {
            for (int j = 0; j < size; j++)
            {
                if (config[i][j] == 0)
                {
                    return {i, j};
                }
            }
        }
        return {-1, -1};
    }

    set<vvi> getChildren()
    {
        set<vvi> children;
        pi position = findBlankTile(this->config);
        int row = position.first, col = position.second;

        int dr[] = {-1, 1, 0, 0};
        int dc[] = {0, 0, -1, 1};
        string directions[] = {"Up", "Down", "Left", "Right"};
        for (int i = 0; i < 4; i++)
        {
            int newRow = row + dr[i];
            int newCol = col + dc[i];

            if (newRow >= 0 && newRow < config.size() && newCol >= 0 && newCol < config.size())
            {
                vvi childConfig = this->config;
                swap(childConfig[row][col], childConfig[newRow][newCol]);
                children.insert(childConfig);
                // cout << "Moving " << directions[i] << endl;
            }
        }
        return children;
    }
};

int calculateRow(int num,int size){
    return (num-1)/size;
}
int calculateCol(int num,int size){
    return (num-1)%size;
}

int calculateHammingDistance(vvi config)
{
    int dist = 0;
    int size = config.size();

    for (int i = 0; i < size; i++)
    {
        for (int j = 0; j < size; j++)
        {
            if (config[i][j] != (i*size+j+1) && config[i][j] != 0)
            {
                dist++;
            }
        }
    }
    return dist;
}

int calculateManhattanDistance(vvi config){
    int dist = 0;
    int size = config.size();

    for (int i=0;i<size;i++){
        for (int j=0;j<size;j++){
            int row = calculateRow(config[i][j],size);
            int col = calculateCol(config[i][j],size);
            if (config[i][j] == 0) continue;
            dist += abs(row-i) + abs(col-j);
        }
    }
    return dist;
}

int calculateEuclideanDistance(vvi config){
    int dist = 0;
    int size = config.size();

    for (int i=0;i<size;i++){
        for (int j=0;j<size;j++){
            int row = (config[i][j]-1)/size;
            int col = (config[i][j]-1)%size;
            if (config[i][j] == 0) continue;
            dist += sqrt(pow(row-i,2) + pow(col-j,2));
        }
    }
    return dist;
}

int calculateLinearConflict(vvi config){
    int rowConflict = 0;
    int colConflict = 0;
    int size = config.size();

    // Row Conflict
    for (int i=0;i<size;i++){
        for (int j=0;j<size;j++){
            int row1 = calculateRow(config[i][j],size);
            int col1 = calculateCol(config[i][j],size);
            if (row1!=i) continue;
            for (int k=j+1;k<size;k++){
                int row2 = calculateRow(config[i][k],size);
                int col2 = calculateCol(config[i][k],size);
                if (row1==row2 && col1>col2){
                    rowConflict++;
                }
            }
        }
    }

    // Column Conflict
    for (int i=0;i<size;i++){
        for (int j=0;j<size;j++){
            int row1 = calculateRow(config[i][j],size);
            int col1 = calculateCol(config[i][j],size);
            if (col1!=j) continue;
            for (int k=i+1;k<size;k++){
                int row2 = calculateRow(config[k][j],size);
                int col2 = calculateCol(config[k][j],size);
                if (col1==col2 && row1>row2){
                    colConflict++;
                }
            }
        }
    }
    int linearConflict = calculateManhattanDistance(config)+2*(rowConflict + colConflict);
    return linearConflict;

}

void printSolutionPath(vector<vvi> solutionPath)
{
    for (auto config : solutionPath)
    {
        cout << endl;
        for (auto row : config)
        {
            for (auto col : row)
            {
                cout << col << " ";
            }
            cout << endl;
        }
    }
}

int main()
{
    int size;
    vvi start, goal;
    priority_queue<Node> pq;
    string inputFile = "input.txt";

    freopen(inputFile.c_str(), "r", stdin);

    cin >> size;
    start.resize(size, vi(size));
    goal.resize(size, vi(size));

    for (int i = 0; i < size; i++)
    {
        for (int j = 0; j < size; j++)
        {
            cin >> start[i][j];
        }
    }
    // Goal state
    for (int i = 0; i < size; i++)
    {
        for (int j = 0; j < size; j++)
        {
            if (i == size - 1 && j == size - 1)
            {
                goal[i][j] = 0;
            }
            else
            {
                goal[i][j] = i * size + j + 1;
            }
        }
    }
    // Array of heuristic functions
    vector<int (*)(vvi)> heuristicFunctions = {calculateHammingDistance, calculateManhattanDistance, calculateEuclideanDistance, calculateLinearConflict};

    int startHeuristic = heuristicFunctions[3](start);
    int explored = 0,expanded = 0;
    Node startNode(start, startHeuristic, 0);
    pq.push(startNode);
    explored++;
    set<vvi> closedList;
    int minMoves = 0;
    vector<vvi> solutionPath;
    while (!pq.empty())
    {
        Node promisingNode = pq.top();
        pq.pop();
        expanded++;
        closedList.insert(promisingNode.config);
        // promisingNode.printConfig();
        // cout<<endl;
        solutionPath.push_back(promisingNode.config);
        if (promisingNode.config == goal)
        {
            // cout << "Goal reached!" << endl;
            minMoves = promisingNode.cost;
            break;
        }
        set<vvi> children = promisingNode.getChildren();
        for (auto child : children)
        {
            int childHeuristic = calculateHammingDistance(child);
            Node newNode(child, childHeuristic, promisingNode.cost + 1);
            if (closedList.find(child) != closedList.end())
            {
                continue;
            }
            pq.push(newNode);
            explored++;
        }
    }

    cout << "Minimum number of moves = " << minMoves << endl;
    printSolutionPath(solutionPath);
    cout << "Number of nodes explored = " << explored << endl;
    cout << "Number of nodes expanded = " << expanded << endl;
}