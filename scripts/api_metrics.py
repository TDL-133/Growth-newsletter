#!/usr/bin/env python3
"""
API Metrics Tracker - Suivi des coûts et métriques d'optimisation
"""

import json
import logging
from datetime import datetime
from typing import Dict, List
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIMetrics:
    """Tracker pour métriques API et coûts"""
    
    # Coûts Anthropic Claude 3.5 Sonnet (par million de tokens)
    ANTHROPIC_COST_PER_M_INPUT = 3.00  # $3 par 1M tokens input
    ANTHROPIC_COST_PER_M_OUTPUT = 15.00  # $15 par 1M tokens output
    
    def __init__(self, metrics_file: str = "metrics/api_costs.json"):
        """Initialise le tracker de métriques"""
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(exist_ok=True)
        
        self.current_session = {
            'start_time': datetime.now().isoformat(),
            'anthropic_calls': 0,
            'anthropic_input_tokens': 0,
            'anthropic_output_tokens': 0,
            'extraction_method_counts': {
                'anthropic_ai': 0,
                'markdown_parser': 0,
                'substack_parser': 0,
                'firecrawl_direct': 0
            },
            'sources_scraped': 0,
            'articles_extracted': 0
        }
    
    def track_anthropic_call(self, input_tokens: int, output_tokens: int, purpose: str = ""):
        """
        Track un appel API Anthropic
        
        Args:
            input_tokens: Nombre de tokens en input
            output_tokens: Nombre de tokens en output
            purpose: Description de l'appel (extraction, ranking, etc.)
        """
        self.current_session['anthropic_calls'] += 1
        self.current_session['anthropic_input_tokens'] += input_tokens
        self.current_session['anthropic_output_tokens'] += output_tokens
        
        if purpose:
            logger.info(f"📊 Anthropic call: {purpose} | In: {input_tokens} | Out: {output_tokens}")
    
    def track_extraction_method(self, method: str, articles_count: int = 1):
        """
        Track la méthode d'extraction utilisée
        
        Args:
            method: anthropic_ai, markdown_parser, substack_parser, firecrawl_direct
            articles_count: Nombre d'articles extraits
        """
        if method in self.current_session['extraction_method_counts']:
            self.current_session['extraction_method_counts'][method] += articles_count
            self.current_session['articles_extracted'] += articles_count
    
    def calculate_costs(self) -> Dict[str, float]:
        """
        Calcule les coûts de la session actuelle
        
        Returns:
            Dict avec détail des coûts
        """
        input_cost = (self.current_session['anthropic_input_tokens'] / 1_000_000) * self.ANTHROPIC_COST_PER_M_INPUT
        output_cost = (self.current_session['anthropic_output_tokens'] / 1_000_000) * self.ANTHROPIC_COST_PER_M_OUTPUT
        
        return {
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': input_cost + output_cost,
            'input_tokens': self.current_session['anthropic_input_tokens'],
            'output_tokens': self.current_session['anthropic_output_tokens'],
            'total_tokens': self.current_session['anthropic_input_tokens'] + self.current_session['anthropic_output_tokens']
        }
    
    def get_optimization_stats(self) -> Dict:
        """
        Statistiques sur l'optimisation (% extraction sans IA)
        
        Returns:
            Dict avec stats d'optimisation
        """
        total_articles = self.current_session['articles_extracted']
        if total_articles == 0:
            return {'optimization_rate': 0, 'ai_free_count': 0}
        
        ai_free_count = (
            self.current_session['extraction_method_counts']['markdown_parser'] +
            self.current_session['extraction_method_counts']['substack_parser'] +
            self.current_session['extraction_method_counts']['firecrawl_direct']
        )
        
        optimization_rate = (ai_free_count / total_articles) * 100
        
        return {
            'optimization_rate': optimization_rate,
            'ai_free_count': ai_free_count,
            'ai_required_count': self.current_session['extraction_method_counts']['anthropic_ai']
        }
    
    def print_summary(self):
        """Affiche un résumé des métriques"""
        costs = self.calculate_costs()
        opt_stats = self.get_optimization_stats()
        
        print("\n" + "="*70)
        print("📊 RÉSUMÉ DES MÉTRIQUES - SESSION ACTUELLE")
        print("="*70)
        
        print(f"\n💰 COÛTS API ANTHROPIC:")
        print(f"   Appels API: {self.current_session['anthropic_calls']}")
        print(f"   Tokens input: {costs['input_tokens']:,}")
        print(f"   Tokens output: {costs['output_tokens']:,}")
        print(f"   Coût input: ${costs['input_cost']:.4f}")
        print(f"   Coût output: ${costs['output_cost']:.4f}")
        print(f"   💵 COÛT TOTAL: ${costs['total_cost']:.4f}")
        
        print(f"\n🚀 OPTIMISATION:")
        print(f"   Articles extraits: {self.current_session['articles_extracted']}")
        print(f"   Sans IA: {opt_stats['ai_free_count']} ({opt_stats['optimization_rate']:.1f}%)")
        print(f"   Avec IA: {opt_stats['ai_required_count']}")
        
        print(f"\n📈 MÉTHODES D'EXTRACTION:")
        for method, count in self.current_session['extraction_method_counts'].items():
            print(f"   {method}: {count}")
        
        print("\n" + "="*70)
    
    def save_metrics(self):
        """Sauvegarde les métriques dans un fichier JSON"""
        self.current_session['end_time'] = datetime.now().isoformat()
        self.current_session['costs'] = self.calculate_costs()
        self.current_session['optimization'] = self.get_optimization_stats()
        
        # Charger l'historique existant
        history = []
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                history = json.load(f)
        
        # Ajouter la session actuelle
        history.append(self.current_session)
        
        # Sauvegarder
        with open(self.metrics_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        logger.info(f"💾 Métriques sauvegardées: {self.metrics_file}")


def main():
    """Test du tracker"""
    metrics = APIMetrics()
    
    # Simuler des appels
    metrics.track_anthropic_call(1500, 800, "Extraction articles")
    metrics.track_anthropic_call(2000, 1200, "Ranking")
    
    metrics.track_extraction_method('markdown_parser', 15)
    metrics.track_extraction_method('anthropic_ai', 10)
    
    metrics.print_summary()
    metrics.save_metrics()


if __name__ == "__main__":
    main()
