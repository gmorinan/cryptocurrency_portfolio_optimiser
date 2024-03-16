# cryptocurrency_portfolio_optimiser
Optimises allocation among the top 250 cryptocurrencies / web3 projects by market cap according to user preferences

### installation

There is a bug when installing cvxpy on a Mac M1 device. To solve this first install cmake via homebrew

```
python -m venv cryopt
source cryopt/bin/activate
brew install cmake
pip install cvxpy
pip install pandas
pip install numpy
pip install streamlit
pip install cvxopt
```