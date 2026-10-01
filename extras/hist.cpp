// hist.cpp - list history commands that start with a prefix (newest first, no duplicates)
// Build: g++ -O2 -std=c++17 -o hist hist.cpp
// Usage: ./hist su
#include <bits/stdc++.h>
using namespace std;

int main(int argc, char* argv[]) {
    if (argc < 2) { cerr << "usage: hist <prefix> [history-file]\n"; return 1; }
    string prefix = argv[1];

    const char* home = getenv("HOME");
    if (!home) { cerr << "HOME is not set\n"; return 1; }

    // Pass a path as argv[2] to read another file, e.g. ~/.zsh_history
    string path = (argc > 2) ? argv[2] : string(home) + "/.bash_history";
    ifstream in(path);
    if (!in) { cerr << "cannot open " << path << "\n"; return 1; }

    vector<string> lines;
    string line;
    while (getline(in, line)) lines.push_back(line);

    unordered_set<string> seen;
    for (int i = (int)lines.size() - 1; i >= 0; --i)
        if (lines[i].rfind(prefix, 0) == 0 && seen.insert(lines[i]).second)
            cout << lines[i] << '\n';
}
