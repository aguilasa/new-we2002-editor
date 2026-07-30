// The legacy squadra / squadra_ml / tattica constructors were empty; the
// members were left uninitialised and filled in by carica_dabin(). Here the
// members carry default initialisers in the header, so a freshly constructed
// Database is zeroed rather than holding stack garbage. That is a deliberate
// difference from the original: it does not change what Load() produces, but
// it makes uninitialised-read bugs reproducible instead of random.

#include "we2002/Team.hpp"

namespace we2002 {

Team::Team() = default;
MlTeam::MlTeam() = default;
Formation::Formation() = default;

}  // namespace we2002
