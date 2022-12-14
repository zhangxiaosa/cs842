//------------------------------------------------------------------------------
// mutate strategy: add qualifier: volatile, const, static
// inputs: used qualifier
//------------------------------------------------------------------------------
#include <sstream>
#include <string>
#include <iostream>
#include <fstream>
#include "clang/AST/AST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/ASTConsumers.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "llvm/Support/raw_ostream.h"
using namespace std;
using namespace clang;
using namespace clang::driver;
using namespace clang::tooling;

static string debug = "";
static string returnTypes = "";

static llvm::cl::OptionCategory ToolingSampleCategory("Tooling Sample");
// By implementing RecursiveASTVisitor, we can specify which AST nodes
// we're interested in by overriding relevant methods.
class MyASTVisitor : public RecursiveASTVisitor<MyASTVisitor> {
public:
  MyASTVisitor(Rewriter &R) : TheRewriter(R) {}

  bool VisitVarDecl(VarDecl *d) {
    return true;
  }

  bool VisitStmt(Stmt *s) {
    return true;
  }

  bool VisitFunctionDecl(FunctionDecl *node) {
    string return_type = node->getReturnType().getAsString();
    string function_name = node->getNameInfo().getAsString();
    string newstr;
    if (debug.compare("true") == 0) {
	cout << "function name: " << function_name << endl;
    	cout << "return type: " << return_type << endl;
	cout << "has body: " << node->hasBody() << endl;
    }
    if (node->hasBody()) {
	Stmt* function_body = node->getBody();
	if (returnTypes.find("void") != string::npos) {
		newstr = "{ return; }";
		TheRewriter.ReplaceText(function_body->getSourceRange(), newstr);
	} 
	else if(returnTypes.find("int") != string::npos
		|| returnTypes.find("singed int") != string::npos
		|| returnTypes.find("unsigned int") != string::npos
		|| returnTypes.find("signed") != string::npos
		|| returnTypes.find("unsigned") != string::npos
		) {
		newstr = "{ return 0; }";
		TheRewriter.ReplaceText(function_body->getSourceRange(), newstr);
	}
	else if(returnTypes.find("float") != string::npos
		|| returnTypes.find("double") != string::npos
		) {
		newstr = "{ return 0.0; }";
		TheRewriter.ReplaceText(function_body->getSourceRange(), newstr);
	}
	else if(returnTypes.find("bool") != string::npos) {
		newstr = "{ return false; }";
		TheRewriter.ReplaceText(function_body->getSourceRange(), newstr);
	}
    }
    return true;
  }

private:
  Rewriter &TheRewriter;
};

// Implementation of the ASTConsumer interface for reading an AST produced
// by the Clang parser.
class MyASTConsumer : public ASTConsumer {
public:
  MyASTConsumer(Rewriter &R) : Visitor(R) {}

  void HandleTranslationUnit(ASTContext &Context) {
    /* we can use ASTContext to get the TranslationUnitDecl, which is
       a single Decl that collectively represents the entire source file */
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());
  }

private:
  MyASTVisitor Visitor;
};

// For each source file provided to the tool, a new FrontendAction is created.
class MyFrontendAction : public ASTFrontendAction {
public:
  MyFrontendAction() {}
  
  void EndSourceFileAction() override {
    SourceManager &SM = TheRewriter.getSourceMgr();
    llvm::errs() << "** EndSourceFileAction for: "
                 << SM.getFileEntryForID(SM.getMainFileID())->getName() << "\n";

    // Now emit the rewritten buffer.
    TheRewriter.overwriteChangedFiles();
  }

  std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI,
                                                 StringRef file) override {
    llvm::errs() << "** Creating AST consumer for: " << file << "\n";
    TheRewriter.setSourceMgr(CI.getSourceManager(), CI.getLangOpts());
    return std::make_unique<MyASTConsumer>(TheRewriter);
  }

private:
  Rewriter TheRewriter;
};

int main(int argc, const char **argv) {
  int cnt = argc;
  for (int i = 0; i < cnt; i++) {
    printf("argv[%d]: %s\n", i, argv[i]);
  }

  debug = argv[3];
  returnTypes = argv[4];

  auto ExpectedParser = CommonOptionsParser::create(argc, argv, ToolingSampleCategory);
  if (!ExpectedParser) {
    // Fail gracefully for unsupported options.
    llvm::errs() << ExpectedParser.takeError();
    return 1;
  }
  CommonOptionsParser& OptionsParser = ExpectedParser.get();
  ClangTool Tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());
  return Tool.run(newFrontendActionFactory<MyFrontendAction>().get());
}
