#include <vector>
#include <string>

string remove_spaces(const string &s);
vector<string> &splitOutsideDelimitingChars(const string &s, char openDelim, char closeDelim, vector<string> &elems);
vector<string> splitOutsideDelimitingChars(const string &s, char openDelim, char closeDelim);
vector<string> &split(const string &s, char delim, vector<string> &elems);
vector<string> split(const string &s, char delim);
string getURLcontent(const string &link);